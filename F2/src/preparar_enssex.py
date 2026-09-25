"""Preparación y validación de los datos de F2, sin gráficos ni documentos."""
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



def sha256_archivo(ruta):
    """Calcula la identidad del archivo sin cargarlo entero en memoria."""
    digest = hashlib.sha256()
    with Path(ruta).open('rb') as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):
            digest.update(bloque)
    return digest.hexdigest()



def sha256_codigo(ruta):
    """Calcula SHA-256 del código con finales de línea normalizados a LF."""
    contenido = Path(ruta).read_bytes()
    contenido = contenido.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    return hashlib.sha256(contenido).hexdigest()



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
    """Calcula diferencia de edad; no exporta duración sin referencia validada."""
    resultado = limpia.copy(deep=True)
    resultado['diferencia_edad_pareja'] = (resultado['p4'] - resultado['p91']).astype('Int64')
    # Las fuentes no definen qué evento representa fecha. No usar el año actual,
    # ni asumir que todas las entrevistas corresponden al año nominal del estudio.
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



def validar_resultado(original, final, matriz, esquema):
    """Invariantes del flujo real: filas, dominios, faltantes, órdenes y derivadas."""
    filas = []
    def exigir(nombre, condicion):
        if not bool(condicion):
            raise AssertionError(nombre)
        filas.append({'comprobacion': nombre, 'resultado': 'OK'})
    originales = [v['nombre'] for v in esquema['variables']]
    esperadas = originales + ['diferencia_edad_pareja']
    exigir('Se conservan todas las personas seleccionadas y su orden', final.index.equals(original.index))
    exigir('19 columnas originales y una derivada calculada', final.columns.tolist() == esperadas)
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
    exigir('Duración sin referencia validada excluida del producto', 'anios_convivencia_aprox' not in final.columns)
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
