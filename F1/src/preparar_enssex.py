"""Preparación reproducible de ENSSEX para F2; el archivo original nunca se edita."""
from pathlib import Path
from importlib.metadata import version
import ast
import csv
import hashlib
import json
import platform
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def sha256_archivo(ruta):
    """Calcula la identidad del archivo sin cargarlo entero en memoria."""
    digest = hashlib.sha256()
    with Path(ruta).open('rb') as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):
            digest.update(bloque)
    return digest.hexdigest()


def huella_tabla(tabla):
    digest = hashlib.sha256(pd.util.hash_pandas_object(tabla, index=True).values.tobytes())
    digest.update(str(list(zip(tabla.columns, tabla.dtypes.astype(str)))).encode())
    return digest.hexdigest()


def verificar_entorno(raiz):
    """Verifica todas las versiones fijadas, sin instalar ni cambiar paquetes."""
    filas = []
    for linea in (Path(raiz) / 'requirements.txt').read_text(encoding='utf-8-sig').splitlines():
        if not linea.strip() or linea.startswith('#'):
            continue
        nombre, esperada = linea.strip().split('==', 1)
        instalada = version(nombre)
        filas.append({'paquete': nombre, 'esperada': esperada, 'instalada': instalada,
                      'coincide': instalada == esperada})
    resultado = pd.DataFrame(filas)
    if resultado.empty or not resultado['coincide'].all():
        raise RuntimeError('El entorno no coincide con requirements.txt. Revisar la instalación.')
    if platform.python_version() != '3.13.15':
        raise RuntimeError('Usar Python 3.13.15, la versión documentada del proyecto.')
    return resultado


def verificar_alineacion_f1(ruta_notebook, esquema):
    """Comprueba nombres, códigos especiales y pregunta frente a la definición de F1."""
    nb = json.loads(Path(ruta_notebook).read_text(encoding='utf-8'))
    configuracion = None
    for celda in nb['cells']:
        if celda['cell_type'] != 'code':
            continue
        for nodo in ast.parse(''.join(celda['source'])).body:
            if isinstance(nodo, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == 'VARIABLES' for t in nodo.targets
            ):
                configuracion = ast.literal_eval(nodo.value)
    esperadas = {v['nombre']: v for v in esquema['variables']}
    if configuracion is None or set(configuracion) != set(esperadas):
        raise ValueError('La selección de F1 y F2 no coincide.')
    for nombre, (_, especiales) in configuracion.items():
        if especiales != esperadas[nombre]['no_respuesta']:
            raise ValueError(f'Códigos especiales distintos en F1 y F2: {nombre}.')
    narrativa = '\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'markdown')
    if esquema['pregunta'] not in narrativa:
        raise ValueError('La pregunta de F2 no coincide con la formulación de F1.')
    return len(esperadas)


def validar_columnas(tabla, requeridas):
    if tabla.empty:
        raise ValueError('No hay registros para procesar.')
    if not tabla.columns.is_unique:
        raise ValueError('Existen nombres de columnas repetidos.')
    faltan = sorted(set(requeridas) - set(tabla.columns))
    if faltan:
        raise ValueError('Faltan columnas: ' + ', '.join(faltan))


def cargar_base(ruta, evidencia, esquema):
    """Verifica identidad y carga la base completa antes de seleccionar personas."""
    ruta = Path(ruta)
    if not ruta.is_file():
        raise FileNotFoundError('Falta el CSV; seguir la guía de obtención y conversión de ENSSEX.')
    if sha256_archivo(ruta) != evidencia['csv_sha256']:
        raise ValueError('El CSV no coincide con la conversión verificada.')
    with ruta.open(encoding='utf-8-sig', newline='') as entrada:
        cabecera = next(csv.reader(entrada, delimiter=';'))
    if len(set(cabecera)) != len(cabecera):
        raise ValueError('Cabecera con nombres duplicados.')
    base = pd.read_csv(ruta, sep=';', encoding='utf-8-sig', keep_default_na=False,
                       na_values=[''], low_memory=False)
    validar_columnas(base, [v['nombre'] for v in esquema['variables']])
    if base.shape != (evidencia['checks']['rows'], evidencia['checks']['columns']):
        raise ValueError('Dimensiones distintas de la base documentada.')
    return base


def perfil_variables(tabla, esquema):
    """Distingue vacíos físicos de respuestas especiales todavía codificadas."""
    filas = []
    for v in esquema['variables']:
        s = tabla[v['nombre']]
        filas.append({'variable': v['nombre'], 'rol': v['rol'], 'tipo_lectura': str(s.dtype),
                      'distintos': int(s.nunique()), 'vacios': int(s.isna().sum()),
                      'no_respuesta': int(s.isin(v['no_respuesta']).sum())})
    return pd.DataFrame(filas)


def seleccionar_convivientes(base, esquema):
    """Aplica ambos filtros y devuelve una copia de las 19 columnas, con conteos."""
    columnas = [v['nombre'] for v in esquema['variables']]
    validar_columnas(base, columnas)
    con_pareja = base['p81'].eq(1)
    convive = con_pareja & base['p83'].eq(1)
    seleccion = base.loc[convive, columnas].copy()
    if seleccion.empty:
        raise ValueError('Ninguna persona cumple simultáneamente p81=1 y p83=1.')
    if seleccion['folio_encuesta'].isna().any() or seleccion['folio_encuesta'].duplicated().any():
        raise ValueError('Revisar los folios; no se eliminan duplicados automáticamente.')
    conteos = pd.DataFrame([
        {'etapa': 'Base completa', 'filas': len(base), 'excluidas_en_paso': 0},
        {'etapa': 'Tiene pareja (p81=1)', 'filas': int(con_pareja.sum()),
         'excluidas_en_paso': int((~con_pareja).sum())},
        {'etapa': 'Además convive (p83=1)', 'filas': len(seleccion),
         'excluidas_en_paso': int(con_pareja.sum()) - len(seleccion)},
    ])
    return seleccion, conteos


def normalizar_variable(serie, especificacion):
    """Convierte NS/NR por pregunta; rechaza valores desconocidos antes del casting."""
    v = especificacion
    if v['tipo'] == 'fecha':
        fechas = pd.to_datetime(serie, format='%d/%m/%Y', errors='coerce')
        if (serie.notna() & fechas.isna()).any():
            raise ValueError('Hay textos de fecha que no siguen día/mes/año.')
        return fechas
    try:
        numero = pd.to_numeric(serie, errors='raise')
    except (ValueError, TypeError) as error:
        raise ValueError(f'Tipo inesperado en {v["nombre"]}.') from error
    # Un mismo código (p. ej. 9) tiene significados distintos según la pregunta.
    numero = numero.mask(numero.isin(v['no_respuesta']))
    presentes = numero.dropna().astype(float)
    if not np.isfinite(presentes).all() or not (presentes == np.floor(presentes)).all():
        raise ValueError(f'Se esperaban enteros finitos en {v["nombre"]}.')
    if v['categorias'] and not numero.dropna().isin(v['categorias']).all():
        raise ValueError(f'Categoría no documentada en {v["nombre"]}.')
    if v['nombre'] == 'p4' and (presentes < 18).any():
        raise ValueError('Edad de persona encuestada fuera de la población adulta.')
    if v['nombre'] == 'p91' and (presentes < 0).any():
        raise ValueError('Edad de pareja negativa.')
    if v['nombre'] == 'p84' and ((presentes < 1) | (presentes > 2023)).any():
        raise ValueError('Año de inicio incompatible con el período de la encuesta.')
    if v['tipo'] == 'identificador':
        if numero.isna().any() or (presentes <= 0).any():
            raise ValueError('Folio ausente o no positivo.')
        return numero.astype('Int64').astype('string')
    return numero.astype('Int64')


def limpiar_codigos(seleccion, esquema):
    """Recodifica sobre una copia y registra cuántas celdas cambian por variable."""
    limpia = seleccion.copy(deep=True)
    filas = []
    for v in esquema['variables']:
        nombre = v['nombre']
        original = seleccion[nombre]
        limpia[nombre] = normalizar_variable(original, v)
        filas.append({'variable': nombre, 'vacios_originales': int(original.isna().sum()),
                      'NS_NR_a_faltante': int(original.isin(v['no_respuesta']).sum()),
                      'faltantes_despues': int(limpia[nombre].isna().sum()),
                      'filas_eliminadas': 0})
    return limpia, pd.DataFrame(filas)


def diagnosticar_tiempo(tabla):
    """Diagnóstico bajo una hipótesis temporal; no valida el significado de fecha."""
    fechas = pd.to_datetime(tabla['fecha'], format='%d/%m/%Y', errors='coerce')
    fuera = fechas.notna() & ~fechas.dt.year.isin([2022, 2023])
    filas = [{'revision': 'Fecha ausente', 'registros': int(tabla['fecha'].isna().sum())},
             {'revision': 'Texto de fecha no interpretable', 'registros': int((tabla['fecha'].notna() & fechas.isna()).sum())},
             {'revision': 'Fecha fuera de 2022–2023', 'registros': int(fuera.sum())}]
    if 'p84' in tabla:
        duracion_hipotetica = fechas.dt.year - pd.to_numeric(tabla['p84'], errors='coerce')
        filas += [
            {'revision': 'Si fecha fuera la referencia: inicio posterior a fecha', 'registros': int(duracion_hipotetica.lt(0).sum())},
            {'revision': 'Si fecha fuera la referencia: duración supera edad de la persona', 'registros': int(duracion_hipotetica.gt(tabla['p4']).sum())},
            {'revision': 'Si fecha fuera la referencia: duración supera edad de la pareja', 'registros': int(duracion_hipotetica.gt(tabla['p91']).sum())},
        ]
    return pd.DataFrame(filas)


def resumen_atipicos(tabla, columnas):
    """Regla 1,5 IQR como señal de revisión, sin borrar ni winsorizar valores."""
    registros = []
    for nombre in columnas:
        x = pd.to_numeric(tabla[nombre], errors='raise').dropna().astype(float).to_numpy()
        if not len(x):
            registros.append({'variable': nombre, 'n': 0, 'min': np.nan, 'Q1': np.nan,
                              'mediana': np.nan, 'Q3': np.nan, 'max': np.nan,
                              'limite_inferior': np.nan, 'limite_superior': np.nan, 'senalados_IQR': 0})
            continue
        q1, mediana, q3 = np.quantile(x, [.25, .5, .75])
        inferior, superior = q1 - 1.5 * (q3-q1), q3 + 1.5 * (q3-q1)
        registros.append({'variable': nombre, 'n': len(x), 'min': float(np.min(x)),
                          'Q1': q1, 'mediana': mediana, 'Q3': q3, 'max': float(np.max(x)),
                          'limite_inferior': inferior, 'limite_superior': superior,
                          'senalados_IQR': int(np.count_nonzero((x < inferior) | (x > superior)))})
    return pd.DataFrame(registros)


def disponibilidad_analisis(limpia, esquema):
    """Muestra denominadores por comparación; no aplica exclusión global."""
    centrales = esquema['centrales']
    originales = [v['nombre'] for v in esquema['variables']]
    grupos = [('Convivientes conservados', []),
              ('Dependencia y valoración de vida sexual', ['p93', 'i_6_p9']),
              ('Dependencia y bienestar emocional', ['p93', 'i_2_p9']),
              ('Tres centrales completas', centrales),
              ('Todas las 19 originales completas', originales)]
    return pd.DataFrame([
        {'criterio': nombre, 'disponibles': int(limpia[cols].notna().all(axis=1).sum()) if cols else len(limpia),
         'no_disponibles': int(limpia[cols].isna().any(axis=1).sum()) if cols else 0}
        for nombre, cols in grupos])


def comparar_imputaciones(limpia, columnas, grupo='p93'):
    """Escenarios contrafactuales sobre copias; ninguno alimenta el dataset final."""
    filas = []
    for nombre in columnas:
        s = limpia[nombre].astype('Float64')
        observados = s.dropna().astype(float)
        var_observada = float(observados.var(ddof=0)) if len(observados) else np.nan
        propuestas = {'Conservar faltantes': s,
                      'Eliminar solo para este cálculo': s.dropna(),
                      'Imputar media global': s.fillna(s.mean()),
                      'Imputar mediana global': s.fillna(s.median())}
        if nombre != grupo:
            # Quienes no tienen p93 válido no reciben una mediana de grupo inventada.
            medianas = s.groupby(limpia[grupo]).transform('median')
            propuestas['Imputar mediana por dependencia'] = s.fillna(medianas)
        for metodo, candidato in propuestas.items():
            valores = candidato.dropna().astype(float)
            var = float(valores.var(ddof=0)) if len(valores) else np.nan
            filas.append({'variable': nombre, 'alternativa': metodo,
                          'filas': len(candidato), 'faltantes': int(candidato.isna().sum()),
                          'imputados': max(0, int(s.isna().sum()-candidato.isna().sum())) if len(candidato)==len(s) else 0,
                          'valores_fraccionarios': int((valores != np.floor(valores)).sum()),
                          'varianza_codigos': var,
                          'cambio_varianza_pct': (100*(var/var_observada-1)) if var_observada > 0 else 0.0})
    return pd.DataFrame(filas)


def construir_derivadas(limpia):
    """Calcula diferencia de edad; reserva duración sin inventar una referencia."""
    resultado = limpia.copy(deep=True)
    resultado['diferencia_edad_pareja'] = (resultado['p4'] - resultado['p91']).astype('Int64')
    # Las fuentes no definen qué evento representa fecha. No usar el año actual,
    # ni asumir que todas las entrevistas corresponden al año nominal del estudio.
    resultado['anios_convivencia_aprox'] = pd.Series(pd.NA, index=resultado.index, dtype='Int64')
    return resultado


def tipificar_categorias(tabla, esquema):
    """Declara categorías y orden analítico; conserva los códigos originales."""
    resultado = tabla.copy(deep=True)
    for v in esquema['variables']:
        if v['categorias']:
            resultado[v['nombre']] = pd.Categorical(resultado[v['nombre']],
                                                    categories=v['categorias'], ordered=v['ordenada'])
    return resultado


def codificar_nominales(tabla, esquema):
    """Matriz auxiliar one-hot: folio y categorías nominales, con NA explícito."""
    nombres = [v['nombre'] for v in esquema['variables']
               if v['tipo'] == 'nominal' and v['rol'] != 'auxiliar']
    # No codificamos folio como predictor ni incluimos los filtros constantes.
    indicadores = pd.get_dummies(tabla[nombres], columns=nombres, prefix_sep='__',
                                dummy_na=True, dtype='uint8')
    indicadores.columns = [re.sub(r'__nan$', '__sin_respuesta', c) for c in indicadores.columns]
    return pd.concat([tabla[['folio_encuesta']], indicadores], axis=1)


def graficar_diagnostico(limpia, impacto, esquema):
    """Visualiza faltantes y tamaños de grupo, sin adelantar inferencias de F3."""
    fig, ejes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    faltan = impacto.loc[impacto['faltantes_despues'].gt(0)].sort_values('faltantes_despues')
    from textwrap import fill
    rotulos = [fill(etiqueta_variable(n, esquema), width=38) for n in faltan['variable']]
    ejes[0].barh(rotulos, 100*faltan['faltantes_despues']/len(limpia), color='#35749A')
    ejes[0].tick_params(axis='y', labelsize=9)
    ejes[0].set(xlabel='Porcentaje de las personas seleccionadas', title='Faltantes después de recodificar NS/NR')
    cantidades = limpia['p93'].value_counts(dropna=False).reindex([1, 2, 3, pd.NA], fill_value=0)
    ejes[1].bar(['Completa', 'Parcial', 'No depende', 'Sin respuesta'], cantidades.to_numpy(), color='#448578')
    ejes[1].set(ylabel='Personas', title='Dependencia económica de la pareja (p93)')
    ejes[1].tick_params(axis='x', rotation=20)
    for eje in ejes:
        eje.spines[['top', 'right']].set_visible(False)
    return fig


def graficar_edades(limpia):
    fig, ejes = plt.subplots(1, 2, figsize=(11, 3.8), constrained_layout=True)
    ejes[0].hist([limpia['p4'].dropna().astype(float), limpia['p91'].dropna().astype(float)],
                 bins=np.arange(15, 106, 5), label=['Persona encuestada (p4)', 'Pareja (p91)'], color=['#35749A', '#D19650'])
    ejes[0].set(xlabel='Edad en años', ylabel='Personas', title='Distribución de las edades')
    ejes[0].legend()
    ejes[1].hist((limpia['p4']-limpia['p91']).dropna().astype(float), bins=30, color='#448578')
    ejes[1].set(xlabel='Edad de la persona (p4) menos edad de la pareja (p91)', ylabel='Personas', title='Diferencia de edad con signo')
    for eje in ejes:
        eje.spines[['top', 'right']].set_visible(False)
    return fig


def validar_resultado(original, final, matriz, esquema):
    """Invariantes del flujo real: filas, dominios, faltantes, órdenes y derivadas."""
    filas = []
    def exigir(nombre, condicion):
        if not bool(condicion):
            raise AssertionError(nombre)
        filas.append({'comprobacion': nombre, 'resultado': 'OK'})
    originales = [v['nombre'] for v in esquema['variables']]
    esperadas = originales + ['diferencia_edad_pareja', 'anios_convivencia_aprox']
    exigir('Se conservan todas las personas seleccionadas y su orden', final.index.equals(original.index))
    exigir('19 columnas originales y 2 espacios para derivadas', final.columns.tolist() == esperadas)
    exigir('Folios presentes y únicos', final['folio_encuesta'].notna().all() and final['folio_encuesta'].is_unique)
    exigir('Filtros de pareja y convivencia', final['p81'].eq(1).all() and final['p83'].eq(1).all())
    for v in esquema['variables']:
        nombre = v['nombre']
        if v['categorias']:
            exigir(f'Dominio y orden de {nombre}',
                   final[nombre].cat.categories.tolist() == v['categorias'] and final[nombre].cat.ordered == v['ordenada'])
        esperados_na = original[nombre].isna() | original[nombre].isin(v['no_respuesta'])
        exigir(f'Faltantes explicados y sin imputación en {nombre}', final[nombre].isna().equals(esperados_na))
        validos = ~esperados_na
        if v['tipo'] not in ['fecha', 'identificador']:
            exigir(f'Respuestas sustantivas conservadas en {nombre}', np.array_equal(
                original.loc[validos, nombre].to_numpy(dtype=float),
                final.loc[validos, nombre].to_numpy(dtype=float)))
        elif v['tipo'] == 'identificador':
            exigir('Folios conservados al convertirlos a texto', np.array_equal(
                original[nombre].to_numpy(dtype=float), pd.to_numeric(final[nombre]).to_numpy(dtype=float)))
        else:
            fechas_antes = pd.to_datetime(original[nombre], format='%d/%m/%Y')
            exigir('Día, mes y año conservados en fecha',
                   fechas_antes.dt.strftime('%Y-%m-%d').equals(final[nombre].dt.strftime('%Y-%m-%d')))
    exigir('Diferencia de edad calculada correctamente',
           final['diferencia_edad_pareja'].equals((final['p4']-final['p91']).astype('Int64')))
    exigir('Duración no calculada sin referencia validada', final['anios_convivencia_aprox'].isna().all())
    exigir('Matriz nominal conserva folios y filas', matriz['folio_encuesta'].equals(final['folio_encuesta']))
    for v in esquema['variables']:
        if v['tipo'] != 'nominal' or v['rol'] == 'auxiliar':
            continue
        nombre = v['nombre']
        bloque = matriz.filter(regex='^'+nombre+'__')
        exigir(f'One-hot completo y exclusivo: {nombre}',
               bloque.isin([0,1]).all().all() and bloque.sum(axis=1).eq(1).all())
        for categoria in v['categorias']:
            exigir(f'One-hot corresponde a {nombre}={categoria}',
                   matriz[f'{nombre}__{categoria}'].eq(1).equals(final[nombre].eq(categoria)))
        exigir(f'One-hot conserva ausencia: {nombre}',
               matriz[f'{nombre}__sin_respuesta'].eq(1).equals(final[nombre].isna()))
    return pd.DataFrame(filas)


def serializar_base(tabla, esquema):
    """Formato portable: códigos enteros, fecha ISO y blancos para faltantes."""
    salida = tabla.copy(deep=True)
    for v in esquema['variables']:
        if v['categorias']:
            salida[v['nombre']] = salida[v['nombre']].astype('Int64')
    return salida


def exportar_resultados(final, matriz, carpeta, esquema):
    """Exporta y vuelve a leer el CSV para verificar valores, nulos y folios."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta/'enssex_convivientes_F2.csv'
    serial = serializar_base(final, esquema)
    serial.to_csv(ruta, sep=';', encoding='utf-8-sig', index=False, na_rep='', date_format='%Y-%m-%d', lineterminator='\n')
    tipos = {c: ('string' if c == 'folio_encuesta' else 'Int64') for c in serial if c != 'fecha'}
    leida = pd.read_csv(ruta, sep=';', encoding='utf-8-sig', dtype=tipos,
                       keep_default_na=False, na_values=[''], parse_dates=['fecha'])
    pd.testing.assert_frame_equal(serial.reset_index(drop=True), leida.reset_index(drop=True),
                                  check_dtype=False, check_exact=True)
    ruta_nom = carpeta/'enssex_convivientes_F2_nominales.csv'
    matriz.to_csv(ruta_nom, sep=';', encoding='utf-8-sig', index=False, lineterminator='\n')
    nom_leida = pd.read_csv(ruta_nom, sep=';', encoding='utf-8-sig', dtype={'folio_encuesta':'string'})
    pd.testing.assert_frame_equal(matriz.reset_index(drop=True), nom_leida, check_dtype=False, check_exact=True)
    return {'principal': {'archivo': ruta.name, 'filas': len(final), 'columnas': len(final.columns), 'sha256': sha256_archivo(ruta)},
            'nominales': {'archivo': ruta_nom.name, 'filas': len(matriz), 'columnas': len(matriz.columns), 'sha256': sha256_archivo(ruta_nom)}}


def tabla_markdown(tabla):
    """Evita una dependencia extra para producir documentación con las cifras reales."""
    def texto(valor):
        if pd.isna(valor):
            return '—'
        if isinstance(valor, (float, np.floating)):
            return f'{valor:.3f}'
        return str(valor).replace('|', '/').replace('\n', ' ')
    lineas = ['| '+' | '.join(map(str,tabla.columns))+' |', '| '+' | '.join(['---']*len(tabla.columns))+' |']
    lineas.extend('| '+' | '.join(texto(v) for v in fila)+' |' for fila in tabla.itertuples(index=False, name=None))
    return '\n'.join(lineas)


def bitacora_decisiones(base, seleccion, limpia, final, matriz, impacto, disponibilidad, atipicos, tiempo):
    """Una fila por decisión con motivo, alternativa descartada y efecto medido."""
    faltantes = int(impacto['NS_NR_a_faltante'].sum())
    completos = int(disponibilidad.loc[disponibilidad['criterio'].eq('Todas las 19 originales completas'), 'disponibles'].iloc[0])
    filas = [
        ('F1-01','F1','Conservar el original y su huella','Mantener trazabilidad de la conversión SAV–CSV','Editar raw en cada fase',f'{len(base)} filas y {len(base.columns)} columnas originales intactas'),
        ('F1-02','F1','Usar 19 columnas: 3 centrales, 12 complementarias y 4 auxiliares','Responder la pregunta y contextualizarla con el alcance acordado','Seleccionar todas las columnas o mezclar los dos resultados','19 seleccionadas; 2 resultados ordinales separados; sin ponderadores ni inferencia poblacional'),
        ('F2-01','F2','Seleccionar p81=1 y p83=1 conjuntamente','La unidad de estudio es la persona que convive con su pareja','Usar solo estado civil o uno de los filtros',f'{len(base)} → {len(seleccion)} personas; {len(base)-len(seleccion)} fuera del alcance'),
        ('F2-02','F2','Comprobar folios antes de limpiar','Una repetición requiere investigación; no elegir arbitrariamente una respuesta','drop_duplicates automático',f'{int(seleccion.folio_encuesta.isna().sum())} folios ausentes; {int(seleccion.folio_encuesta.duplicated().sum())} repetidos; 0 filas eliminadas'),
        ('F2-03','F2','Convertir NS/NR según cada pregunta','Los códigos especiales no son respuestas sustantivas y contaminan los cálculos','Reemplazar 8, 9 o 99 globalmente',f'{faltantes} celdas recodificadas; 0 cambios en regiones válidas, estado civil 8 e ingreso relativo 6'),
        ('F2-04','F2','Conservar faltantes y usar denominadores por comparación','Evitar atribuir una respuesta íntima no observada; la sensibilidad muestra efectos de imputar','Eliminar toda fila incompleta o imputar media/mediana',f'0 valores imputados; 0 personas eliminadas por faltantes; casos completos globales conservarían {completos} de {len(seleccion)}'),
        ('F2-05','F2','Conservar extremos y registrar señales de revisión','La regla IQR detecta rareza, no demuestra error; no hay fuente para corregir las edades','Eliminar o winsorizar por IQR',f'{int(atipicos.senalados_IQR.sum())} señales variable-persona en {len(atipicos)} variables, no personas únicas; 0 recortes'),
        ('F2-06','F2','Tipificar ordinales con orden explícito y nominales sin orden','El tipo de almacenamiento no define la escala de medición','Orden alfabético o tratar códigos nominales como cantidades','5 ordinales con orden de códigos declarado; p93 aumenta hacia menor dependencia; nominales conservan significado'),
        ('F2-07','F2','Calcular p4 menos p91','Diferencia interpretable en años, conservando el signo','Restar códigos de no respuesta o usar valor absoluto',f'{int(final.diferencia_edad_pareja.notna().sum())} diferencias calculadas; rango {final.diferencia_edad_pareja.min()} a {final.diferencia_edad_pareja.max()} años'),
        ('F2-08','F2','Dejar duración de convivencia sin calcular','fecha tiene formato válido, pero su evento de referencia no está documentado','Asumir fecha de entrevista, usar año actual o 2022 para todas las personas',f'{len(final)} ausencias técnicas en anios_convivencia_aprox; no son no respuestas de la encuesta'),
        ('F2-09','F2','Exportar one-hot en una matriz auxiliar','Dar una representación numérica a las nominales sin inventar distancias','Reemplazar el dataset interpretable por dummies o usar folio como predictor',f'{len(matriz)} filas; {len(matriz.columns)-1} indicadores más folio; 1 indicador explícito de ausencia por variable'),
        ('F2-10','F2','Mantener edades y diferencia en años; no escalar','El alcance actual es descriptivo; no hay algoritmo basado en distancias que necesite escalamiento','Normalizar automáticamente todas las columnas','0 columnas escaladas; códigos ordinales no tratados como mediciones continuas'),
        ('F2-11','F2','Exportar CSV con esquema y comprobar su relectura','CSV no conserva categorías de pandas; el diccionario declara tipos, orden y ausencias','Entregar solo un CSV sin significado de los códigos',f'{len(final)} filas × {len(final.columns)} columnas; 19 originales preparadas + diferencia calculada + duración reservada'),
    ]
    return pd.DataFrame(filas,columns=['id','fase','decision','motivo','alternativa_descartada','impacto'])


def documentar_resultados(carpeta, esquema, resumen, tablas, bitacora, final):
    """Genera las cifras para el informe desde los mismos resultados del notebook."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta/'validacion_F2.json').write_text(json.dumps(resumen,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    contenido = '# Bitácora de decisiones de F1 y F2\n\n'
    contenido += 'Los antecedentes de F1 se contrastan con su notebook y con la evidencia de conversión. Los impactos de F2 se calculan en cada ejecución. Las dos valoraciones se mantienen separadas; el alcance es descriptivo y comparativo de la muestra, sin ponderación.\n\n'
    contenido += tabla_markdown(presentar_tabla(bitacora, esquema))+'\n\n'
    contenido += 'Las imputaciones se evaluaron solo como escenarios de sensibilidad; ninguna se aplicó. La duración de convivencia queda sin calcular hasta documentar una referencia temporal válida.\n'
    (carpeta/'Bitacora_decisiones_F1_F2.md').write_text(contenido,encoding='utf-8')
    texto = '# Resultados de la preparación de ENSSEX\n\n'+esquema['pregunta']+'\n\n'
    texto += (f"Se conservan {len(final):,} personas seleccionadas con p81=1 y p83=1. El conjunto principal tiene 21 columnas: las 19 originales preparadas, la diferencia de edad calculada y el espacio reservado para los años de convivencia. Este último permanece sin valores por falta de una referencia temporal documentada. No debe incluirse en el cálculo de completitud de respuestas originales.\n\n")
    texto += 'No se imputan respuestas ni se eliminan personas por no respuesta o por extremos estadísticos. Los códigos originales y sus motivos de ausencia se pueden recuperar en raw mediante folio_encuesta. Cada análisis posterior debe indicar sus propios casos válidos y no interpretar estas cifras como estimaciones poblacionales.\n\n'
    for titulo, tabla in tablas.items():
        texto += '## '+titulo+'\n\n'+tabla_markdown(presentar_tabla(tabla, esquema))+'\n\n'
    texto += '## Límites y continuidad\n\nLa varianza de códigos en los escenarios de imputación es un diagnóstico mecánico de sensibilidad; no demuestra que las escalas ordinales tengan intervalos iguales. Las señales temporales calculadas bajo la hipótesis de que fecha fuera la referencia tampoco confirman errores por sí solas. Los casos extremos permanecen para revisión y análisis de sensibilidad en F3.\n\n'
    texto += '## Ubicación de los productos\n\nLos CSV se generan en F1/data/processed. La configuración y el diccionario están en F2/docs/esquema_variables_F2.json y Diccionario_procesado_F2.md. La bitácora y validacion_F2.json permiten contrastar estas cifras con las salidas del notebook.\n'
    (carpeta/'Resultados_preparacion_F2.md').write_text(texto,encoding='utf-8')
    filas=[]
    for v in esquema['variables']:
        filas.append({'variable':etiqueta_variable(v['nombre'], esquema),'rol':v['rol'],'tipo_en_memoria':str(final[v['nombre']].dtype),
                      'descripcion':v['descripcion'],'codigos_validos':'; '.join(f'{k}={val}' for k,val in v['etiquetas'].items()) or v['tipo'],
                      'NS_NR_en_raw':str(v['no_respuesta']),'orden':str(v['categorias']) if v['ordenada'] else 'Sin orden nominal / no aplica',
                      'faltantes':int(final[v['nombre']].isna().sum())})
    for nombre in ['diferencia_edad_pareja','anios_convivencia_aprox']:
        filas.append({'variable':etiqueta_variable(nombre, esquema),'rol':'derivada','tipo_en_memoria':'Int64','descripcion':esquema['derivadas'][nombre],
                      'codigos_validos':'Enteros con signo' if nombre.startswith('diferencia') else 'Sin calcular',
                      'NS_NR_en_raw':'No aplica','orden':'No aplica','faltantes':int(final[nombre].isna().sum())})
    dic = '# Diccionario del conjunto procesado de F2\n\n'
    dic += '19 columnas originales preparadas y dos columnas derivadas, una calculada y otra reservada sin valores. CSV: separador punto y coma, UTF-8 con BOM, sin índice, fecha ISO AAAA-MM-DD, códigos enteros y campos vacíos para ausencias. El folio se lee como texto. Para reconstruir categorías y su orden se utiliza esquema_variables_F2.json.\n\n'
    dic += tabla_markdown(pd.DataFrame(filas))+'\n\n'
    dic += 'La matriz auxiliar nominal contiene folio_encuesta y columnas nombre__codigo, más nombre__sin_respuesta para cada nominal. Cada bloque suma uno por persona. Los indicadores no aumentan la selección sustantiva de 19 variables y no forman parte del CSV principal de 21 columnas.\n'
    (carpeta/'Diccionario_procesado_F2.md').write_text(dic,encoding='utf-8')
    (carpeta/'Seleccion_y_justificacion_variables_F2.md').write_text('# Selección de variables de ENSSEX\n\n'+documentar_seleccion(esquema),encoding='utf-8')
    readme = '''# Fase 2 · Limpieza y transformación de ENSSEX

La preparación utiliza la selección acordada de 19 columnas originales y conserva por separado los dos resultados de bienestar. El alcance es descriptivo y comparativo de la muestra, sin ponderación ni interpretación causal.

## Ejecución

1. Preparar el entorno siguiendo la [guía de instalación](../F1/docs/Instalacion_y_ejecucion.md).
2. Disponer del CSV original según la [guía de obtención](../F1/docs/Obtencion_y_conversion_ENSSEX.md).
3. Abrir [F2_limpieza_transformacion_ENSSEX.ipynb](notebooks/F2_limpieza_transformacion_ENSSEX.ipynb) desde JupyterLab.
4. Seleccionar **Python (grupo9-mcdi500)** y usar **Kernel → Restart Kernel and Run All Cells**.
5. Revisar las tablas de evidencia y el cierre, que debe indicar OK en sus siete comprobaciones.

El notebook explica por qué se conserva cada una de las 19 columnas, junto con su nombre y pregunta asociada. Las tablas y gráficos muestran nombres comprensibles y códigos para facilitar su lectura.

El notebook se ejecuta desde F2/notebooks. No necesita variables de una sesión de F1. La semilla declarada es 42; el flujo es determinista y no realiza muestreo. Cada ejecución regenera los CSV y la documentación de resultados.

## Productos y resultados

'''
    readme += f"- {len(final):,} personas con p81=1 y p83=1.\n- {resumen['limpieza']['NS_NR_recodificados']} celdas NS/NR recodificadas; 0 imputaciones y 0 filas eliminadas por faltantes o extremos.\n"
    readme += f"- Conjunto principal: {len(final.columns)} columnas; las 19 originales preparadas, diferencia de edad calculada y duración reservada sin valores.\n"
    readme += f"- Matriz nominal auxiliar: {resumen['exportados']['nominales']['columnas']} columnas, incluido el folio.\n"
    readme += f"- {resumen['validaciones']['invariantes']} invariantes, {resumen['validaciones']['casos_controlados']} casos controlados y relectura completa de ambos CSV verificados.\n\n"
    readme += '''Los CSV `enssex_convivientes_F2.csv` y `enssex_convivientes_F2_nominales.csv` se generan en `F1/data/processed`, se incluyen en el repositorio para facilitar su revisión y pueden reconstruirse ejecutando este notebook. Se conservan las carpetas compartidas `F1/data` y `F1/src` del proyecto.

## Documentación y código

- [Bitácora de decisiones y alternativas](docs/Bitacora_decisiones_F1_F2.md).
- [Resultados para integrar en el informe](docs/Resultados_preparacion_F2.md).
- [Diccionario del conjunto procesado](docs/Diccionario_procesado_F2.md).
- [Selección y justificación de las 19 columnas](docs/Seleccion_y_justificacion_variables_F2.md).
- [Configuración de variables](docs/esquema_variables_F2.json).
- [Evidencia de validación](docs/validacion_F2.json).
- [Funciones de preparación](../F1/src/preparar_enssex.py).
- [Casos controlados de validación](../F1/src/validar_preparacion_enssex.py).

## Límites

La duración de convivencia no se calcula: las fuentes consultadas no definen el evento que representa `fecha`. Sus ausencias son técnicas y no deben mezclarse con no respuestas de la encuesta. Se conservan los extremos estadísticos con su diagnóstico; no se declaran errores sin respaldo.
'''
    (carpeta.parent/'README.md').write_text(readme,encoding='utf-8')


def etiqueta_variable(nombre, esquema):
    """Nombre comprensible y código técnico, sin renombrar columnas del dataset."""
    nombres = {v['nombre']: v['nombre_legible'] for v in esquema['variables']}
    nombres.update({'diferencia_edad_pareja': 'Diferencia de edad con la pareja',
                    'anios_convivencia_aprox': 'Años aproximados de convivencia'})
    return f'{nombres[nombre]} ({nombre})' if nombre in nombres else nombre


def rotular_referencias(texto, esquema):
    """Explica códigos aislados dentro de una salida destinada a lectura humana."""
    nombres = [v['nombre'] for v in esquema['variables']] + ['diferencia_edad_pareja', 'anios_convivencia_aprox']
    patron = r'(?<![\w])(' + '|'.join(re.escape(n) for n in sorted(nombres, key=len, reverse=True)) + r')(?![\w])'
    return re.sub(patron, lambda m: etiqueta_variable(m.group(0), esquema), str(texto))


def presentar_tabla(tabla, esquema):
    """Prepara solo la vista: nombres de preguntas y etiquetas; no altera los datos."""
    vista = tabla.copy(deep=True)
    por_nombre = {v['nombre']: v for v in esquema['variables']}
    for columna in vista:
        if columna == 'variable':
            vista[columna] = vista[columna].map(lambda v: etiqueta_variable(v, esquema))
        elif columna in por_nombre and por_nombre[columna]['categorias']:
            etiquetas = por_nombre[columna]['etiquetas']
            vista[columna] = vista[columna].map(
                lambda v: 'Sin respuesta' if pd.isna(v) else f'{etiquetas.get(str(int(v)), str(v))} ({int(v)})')
        elif vista[columna].dtype == 'object' or pd.api.types.is_string_dtype(vista[columna].dtype):
            # Las preguntas y motivos originales ya se presentan junto a un nombre
            # completo. No se altera su redacción al preparar las tablas de selección.
            if columna not in ['Pregunta o nombre del dato', 'Por qué la conservamos']:
                vista[columna] = vista[columna].map(
                    lambda v: rotular_referencias(v, esquema) if isinstance(v, str) else v)
    vista = vista.rename(columns={n: etiqueta_variable(n, esquema) for n in por_nombre if n in vista.columns})
    vista = vista.rename(columns={
        'variable': 'Variable (nombre y código)', 'rol': 'Función',
        'tipo_lectura': 'Tipo al leer el archivo', 'tipo_analitico': 'Tipo analítico',
        'distintos': 'Valores distintos', 'vacios': 'Campos vacíos', 'no_respuesta': 'Respuestas especiales',
        'codigos_observados': 'Códigos observados', 'no_respuesta_documentada': 'Códigos de no respuesta',
        'vacios_originales': 'Vacíos originales', 'NS_NR_a_faltante': 'NS/NR convertidos en ausencias',
        'faltantes_despues': 'Faltantes después', 'filas_eliminadas': 'Filas eliminadas',
        'vida_sexual_valida': 'Valoraciones válidas de vida sexual',
        'bienestar_emocional_valido': 'Valoraciones válidas de bienestar emocional',
        'porcentaje_faltante': 'Porcentaje de faltantes',
        'categorias_documentadas': 'Categorías documentadas',
        'indicadores_incluida_ausencia': 'Indicadores, incluida ausencia',
        'varianza_codigos': 'Varianza de códigos', 'cambio_varianza_pct': 'Cambio de varianza (%)',
        'valores_fraccionarios': 'Valores fraccionarios', 'senalados_IQR': 'Casos señalados por IQR',
        'limite_inferior': 'Límite inferior IQR', 'limite_superior': 'Límite superior IQR',
    })
    return vista


def documentar_seleccion(esquema):
    """Justificación legible por columna, compartida por notebook y documentación."""
    texto = '''## Por qué seleccionamos estas 19 columnas

La pregunta necesita identificar a las personas que conviven con su pareja y comparar dos valoraciones de bienestar entre los niveles de dependencia económica. Ese es el núcleo del estudio. Conservamos además datos que permiten describir a esas personas, contextualizar futuras comparaciones y comprobar la calidad de los registros.

La selección se organiza por su utilidad concreta:

- **3 centrales:** una define los grupos de dependencia económica y dos registran las valoraciones que se compararán por separado.
- **12 complementarias:** describen el contexto sociodemográfico, de la relación y de salud. Su conservación permite evaluar análisis posteriores sin volver a seleccionar datos del archivo completo.
- **4 auxiliares:** dos definen quién pertenece a la población, una identifica cada registro y una permite revisar una posible referencia temporal.

**No todas las 19 columnas son necesarias en cada comparación.** Para delimitar la población y abordar la pregunta básica utilizamos las tres centrales y los dos filtros de pareja y convivencia. Las demás cumplen una función de contexto o de control técnico. No se eligieron porque ya hayan demostrado una asociación con el bienestar ni porque deban entrar juntas en un modelo. Cada uso posterior dependerá de su pertinencia y de la calidad de las respuestas.

Las tablas indican la pregunta asociada, con ajustes menores de redacción ya documentados en F1. Región, identificador y fecha son campos de la base; no se presentan como preguntas numeradas al encuestado. El código se mantiene entre paréntesis para poder localizar cada columna en el archivo.

'''
    grupos = [('Centrales: qué comparamos y entre qué grupos', 'central'),
              ('Complementarias: características sociodemográficas', 'sociodemografica'),
              ('Complementarias: relación de pareja y salud', 'relacion_salud'),
              ('Auxiliares: población y trazabilidad', 'auxiliar')]
    for titulo, grupo in grupos:
        filas = [{'Variable y código': etiqueta_variable(v['nombre'], esquema),
                  'Pregunta o nombre del dato': v['descripcion'],
                  'Por qué la conservamos': v['justificacion']}
                 for v in esquema['variables'] if v['grupo_explicativo'] == grupo]
        texto += '### ' + titulo + '\n\n' + tabla_markdown(pd.DataFrame(filas)) + '\n\n'
    texto += '''### Qué aporta esta selección a las siguientes fases

En F2 comprobamos la disponibilidad y calidad de estas columnas. En F3 podremos comparar cada valoración entre los grupos de dependencia, describir la composición de esos grupos y evaluar análisis por características personales o de la relación, siempre que existan suficientes respuestas válidas. Conservar una columna no la convierte automáticamente en una causa, un predictor o una variable de ajuste obligatoria.

La edad de la persona encuestada (p4) y la edad de su pareja (p91) permiten calcular la diferencia de edad. El año de inicio de convivencia (p84) y la fecha registrada (fecha) permitirían calcular una duración aproximada solo si se confirma una referencia temporal válida. Por eso conservamos esos datos, pero los años de convivencia permanecen sin calcular. Estas dos derivadas se explican aparte de las 19 columnas originales.

'''
    return texto
