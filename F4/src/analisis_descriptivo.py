"""Tablas reproducibles de F4 con denominadores específicos por valoración."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'F4/src'))
from datos_interpretables import leer_interpretables, CSV, REGISTRO
from preparar_enssex import sha256_archivo

DEPENDENCIA = 'p93'  # Dependencia económica de la pareja.
SEXO = 'p1'  # Sexo asignado al nacer; distinto de género declarado.
VALORACIONES = ('i_6_p9', 'i_2_p9')  # Vida sexual y bienestar mental o emocional.
ARCHIVOS_TABLAS = {
    'dependencia': 'dependencia_economica.csv',
    'denominadores': 'denominadores.csv',
    'i_6_p9': 'valoracion_vida_sexual.csv',
    'i_2_p9': 'bienestar_mental_emocional.csv',
    'dependencia_sexo': 'dependencia_economica_por_sexo.csv',
    'denominadores_sexo': 'denominadores_por_sexo.csv',
    'i_6_p9_sexo': 'valoracion_vida_sexual_por_sexo.csv',
    'i_2_p9_sexo': 'bienestar_mental_emocional_por_sexo.csv',
}


def porcentaje(conteo, denominador):
    """Con base cero no existe un porcentaje: se registra None, nunca cero."""
    return 100.0 * conteo / denominador if denominador else None


def nombre_variable(variable):
    """Acompaña siempre el identificador de pregunta con su descripción."""
    return f"{variable['nombre_legible']} ({variable['nombre']})"


def _validar_entrada(tabla, esquema):
    """Rechaza categorías o identificadores inconsistentes antes de contar."""
    variables = {v['nombre']: v for v in esquema['variables']}
    requeridas = ['folio_encuesta', DEPENDENCIA, *VALORACIONES, SEXO]
    if not tabla.columns.is_unique or not set(requeridas).issubset(tabla.columns):
        raise ValueError('Faltan columnas requeridas o hay nombres duplicados.')
    if tabla['folio_encuesta'].isna().any() or not tabla['folio_encuesta'].is_unique:
        raise ValueError('Los folios deben estar presentes y ser únicos.')
    for codigo in [DEPENDENCIA, *VALORACIONES, SEXO]:
        v = variables[codigo]
        serie = tabla[codigo]
        if (not isinstance(serie.dtype, pd.CategoricalDtype)
                or serie.cat.categories.tolist() != v['categorias']
                or serie.cat.ordered != v['ordenada']):
            raise ValueError(f'{nombre_variable(v)}: restaurar categorías y orden antes del análisis.')
    return variables


def _resumen_base(tabla, variables):
    """Cuenta sin imputar ni eliminar globalmente filas por valores ausentes.

    Recibe la copia restaurada por leer_interpretables y las variables del esquema. Cada
    comparación usa dependencia y valoración válidas; los porcentajes son
    internos a cada grupo. Conserva grupos y respuestas sin observaciones.
    """
    dep = variables[DEPENDENCIA]
    dependencia_presente = tabla[DEPENDENCIA].notna()
    total = len(tabla)
    base_dependencia = int(dependencia_presente.sum())
    distribucion = []
    for codigo in dep['categorias']:
        cantidad = int(tabla[DEPENDENCIA].eq(codigo).sum())
        distribucion.append({
            'variable': nombre_variable(dep), 'codigo_grupo': codigo,
            'grupo': dep['etiquetas'][str(codigo)], 'personas': cantidad,
            'denominador': base_dependencia,
            'porcentaje': porcentaje(cantidad, base_dependencia),
        })
    assert sum(f['personas'] for f in distribucion) == base_dependencia
    comparaciones = {}
    for codigo_variable in VALORACIONES:
        v = variables[codigo_variable]
        presente = tabla[codigo_variable].notna()
        base = int((dependencia_presente & presente).sum())
        ausentes_variable = int((~presente).sum())
        ausentes_ambas = int((~dependencia_presente & ~presente).sum())
        denominadores, distribuciones = [], []
        for codigo in dep['categorias']:
            grupo = tabla.loc[tabla[DEPENDENCIA].eq(codigo), codigo_variable]
            validos = int(grupo.notna().sum())
            ausentes = int(grupo.isna().sum())
            conteos = grupo.value_counts().reindex(v['categorias'], fill_value=0)
            denominadores.append({
                'variable': nombre_variable(v), 'agrupacion': nombre_variable(dep),
                'codigo_grupo': codigo, 'grupo': dep['etiquetas'][str(codigo)],
                'total_grupo': len(grupo), 'validos': validos, 'ausentes': ausentes,
                'porcentaje_ausentes_grupo': porcentaje(ausentes, len(grupo)),
            })
            for categoria in v['categorias']:
                distribuciones.append({
                    'variable': nombre_variable(v), 'agrupacion': nombre_variable(dep),
                    'codigo_grupo': codigo, 'grupo': dep['etiquetas'][str(codigo)],
                    'codigo_respuesta': categoria, 'respuesta': v['etiquetas'][str(categoria)],
                    'personas': int(conteos[categoria]), 'denominador': validos,
                    'porcentaje': porcentaje(int(conteos[categoria]), validos),
                })
            assert int(conteos.sum()) == validos
            assert validos + ausentes == len(grupo)
            if validos:
                suma = sum(f['porcentaje'] for f in distribuciones if f['codigo_grupo'] == codigo)
                assert abs(suma - 100.0) < 1e-9
        assert sum(f['validos'] for f in denominadores) == base
        assert sum(f['total_grupo'] for f in denominadores) == base_dependencia
        assert total - base == total - base_dependencia + ausentes_variable - ausentes_ambas
        comparaciones[codigo_variable] = {
            'variable': nombre_variable(v), 'base_comparacion': base,
            'excluidos_comparacion': total - base,
            'ausentes_valoracion_total': ausentes_variable,
            'ausentes_ambas_variables': ausentes_ambas,
            'denominadores': denominadores, 'distribucion': distribuciones,
        }
    presentes_todas = tabla[[DEPENDENCIA, *VALORACIONES]].notna().all(axis=1)
    return {
        'personas': total,
        'dependencia': {'variable': nombre_variable(dep), 'validos': base_dependencia,
                       'ausentes': total - base_dependencia, 'distribucion': distribucion},
        'comparaciones': comparaciones,
        'base_comun': {'personas': int(presentes_todas.sum()),
                      'uso': 'Referencia disponible; no es la base de las figuras por dimensión.',
                      'grupos': [{'grupo': dep['etiquetas'][str(c)],
                                  'personas': int((presentes_todas & tabla[DEPENDENCIA].eq(c)).sum())}
                                 for c in dep['categorias']]},
    }


def construir_resumen(tabla, esquema):
    """Conserva el total y desagrega por sexo asignado al nacer (p1).

    La desagregación usa las categorías del esquema y denominadores propios
    por sexo, dependencia y dimensión. Las ausencias de sexo permanecen en el
    total y se contabilizan por separado; no se asignan a hombre o mujer.
    """
    variables = _validar_entrada(tabla, esquema)
    resumen = _resumen_base(tabla, variables)
    sexo = variables[SEXO]
    grupos = []
    for codigo in sexo['categorias']:
        subtotal = _resumen_base(tabla.loc[tabla[SEXO].eq(codigo)], variables)
        grupos.append({'codigo_sexo': codigo, 'sexo': sexo['etiquetas'][str(codigo)], **subtotal})
    sin_respuesta = _resumen_base(tabla.loc[tabla[SEXO].isna()], variables)
    partes = [*grupos, sin_respuesta]
    assert sum(g['personas'] for g in partes) == resumen['personas']
    for i, fila in enumerate(resumen['dependencia']['distribucion']):
        assert sum(g['dependencia']['distribucion'][i]['personas'] for g in partes) == fila['personas']
    for codigo in VALORACIONES:
        general = resumen['comparaciones'][codigo]
        assert sum(g['comparaciones'][codigo]['base_comparacion'] for g in partes) == general['base_comparacion']
        for i, fila in enumerate(general['distribucion']):
            assert sum(g['comparaciones'][codigo]['distribucion'][i]['personas'] for g in partes) == fila['personas']
    resumen.update({
        'version': 2,
        'metodologia': {
            'alcance': 'Descriptivo de la muestra, sin ponderación ni extrapolación nacional.',
            'dependencia': 'Porcentajes entre respuestas válidas de dependencia económica.',
            'valoraciones': 'Porcentajes entre respuestas válidas dentro de cada grupo de dependencia.',
            'desagregacion': 'Sexo asignado al nacer (p1); denominador propio por sexo y dependencia.',
            'sexo_ausente': 'Se conserva en el total y se informa aparte; no se asigna a hombre o mujer.',
            'ausencias': 'Exclusión específica por comparación; sin imputación ni eliminación global.',
            'base_cero': 'Porcentaje no calculable: null en JSON, vacío en CSV y sin base en figuras.',
            'escala': 'Siete categorías ordinales; sin agrupación arbitraria ni indicador combinado.',
        },
        'variables': {c: variables[c] for c in [DEPENDENCIA, *VALORACIONES, SEXO]},
        'por_sexo': {'variable': nombre_variable(sexo), 'grupos': grupos, 'sin_respuesta': sin_respuesta},
    })
    return resumen


def tablas_exportables(resumen):
    """Devuelve tablas generales y desagregadas, identificadas con sus descripciones."""
    tablas = {'dependencia': resumen['dependencia']['distribucion'],
              'denominadores': [f for c in resumen['comparaciones'].values() for f in c['denominadores']]}
    tablas.update({c: resumen['comparaciones'][c]['distribucion'] for c in VALORACIONES})
    for nombre in ['dependencia_sexo', 'denominadores_sexo', *[c + '_sexo' for c in VALORACIONES]]:
        tablas[nombre] = []
    # Incluir explícitamente las ausencias de sexo evita perderlas en el respaldo.
    partes = [*resumen['por_sexo']['grupos'],
              {'codigo_sexo': None, 'sexo': 'Sin respuesta', **resumen['por_sexo']['sin_respuesta']}]
    for parte in partes:
        contexto = {'desagregacion': resumen['por_sexo']['variable'],
                    'codigo_sexo': parte['codigo_sexo'], 'sexo': parte['sexo']}
        tablas['dependencia_sexo'].extend({**contexto, **f} for f in parte['dependencia']['distribucion'])
        for codigo in VALORACIONES:
            comparacion = parte['comparaciones'][codigo]
            tablas['denominadores_sexo'].extend({**contexto, **f} for f in comparacion['denominadores'])
            tablas[codigo + '_sexo'].extend({**contexto, **f} for f in comparacion['distribucion'])
    return tablas


def exportar_analisis(entrada, salida):
    """Relee datos verificados y exporta tablas, figuras y registro a carpeta vacía."""
    from visualizaciones import crear_figuras, guardar_figuras
    import matplotlib

    entrada, salida = Path(entrada), Path(salida)
    if salida.exists() and any(salida.iterdir()):
        raise FileExistsError('El destino contiene archivos; elegir una carpeta nueva para el análisis.')
    tabla = leer_interpretables(entrada)
    registro_entrada = json.loads((entrada / REGISTRO).read_text(encoding='utf-8'))
    resumen = construir_resumen(tabla, registro_entrada['esquema'])
    tablas = tablas_exportables(resumen)
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, filas in tablas.items():
        tabla_salida = pd.DataFrame(filas)
        if 'codigo_sexo' in tabla_salida:
            tabla_salida['codigo_sexo'] = tabla_salida['codigo_sexo'].astype('Int64')
        tabla_salida.to_csv(salida / ARCHIVOS_TABLAS[nombre], sep=';',
                            encoding='utf-8-sig', index=False, na_rep='', lineterminator='\n')
    guardar_figuras(crear_figuras(resumen), salida)
    resumen['reproduccion'] = {
        'fecha_utc': datetime.now(timezone.utc).isoformat(),
        'entorno': {'python': platform.python_version(), 'pandas': pd.__version__,
                    'numpy': np.__version__, 'matplotlib': matplotlib.__version__},
        'entradas': {n: sha256_archivo(entrada / n) for n in [CSV, REGISTRO]},
        'codigo': {f'F4/src/{n}': sha256_archivo(RAIZ / 'F4/src' / n)
                   for n in ['datos_interpretables.py', 'analisis_descriptivo.py', 'visualizaciones.py']},
        'productos': {p.name: sha256_archivo(p) for p in sorted(salida.iterdir()) if p.is_file()},
        'comprobaciones': 'Conteos, ausencias, bases por grupo y sexo, porcentajes y conciliación con el total correctos.',
    }
    (salida / 'resumen_analitico.json').write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
        encoding='utf-8', newline='\n')
    return resumen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', type=Path, default=RAIZ / 'F4/data/processed')
    parser.add_argument('--salida', type=Path, default=RAIZ / 'F4/resultados_locales')
    args = parser.parse_args()
    resumen = exportar_analisis(args.entrada, args.salida)
    print(f"OK: {resumen['personas']} personas; conteos y porcentajes verificados.")
    dep = resumen['dependencia']
    print(f"{dep['variable']}: {dep['validos']} válidas y {dep['ausentes']} ausentes.")
    for comparacion in resumen['comparaciones'].values():
        print(f"{comparacion['variable']}: base de comparación = {comparacion['base_comparacion']}.")
    sexo = resumen['por_sexo']
    print(f"{sexo['variable']}: " + '; '.join(f"{g['sexo']} = {g['personas']}" for g in sexo['grupos'])
          + f"; sin respuesta = {sexo['sin_respuesta']['personas']}.")
    print('OK: ocho tablas, tres figuras en PNG/SVG y registro de reproducción.')


if __name__ == '__main__':
    main()
