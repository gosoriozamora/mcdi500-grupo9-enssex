"""Comparación reproducible de lectura SAV. No modifica el flujo de F2 o F3."""
import gc
import timeit
import tracemalloc

import pandas as pd
import pyreadstat


CAMPOS_METADATA = (
    'column_names_to_labels', 'variable_value_labels', 'missing_ranges',
    'original_variable_types', 'readstat_variable_types', 'variable_measure',
)


def _leer(ruta, columnas, parcial):
    """Devuelve las columnas en orden solicitado y sus metadatos relevantes."""
    columnas = list(columnas)
    if not columnas or not all(isinstance(c, str) for c in columnas):
        raise ValueError('Solicitar al menos una columna mediante nombres de texto.')
    if len(columnas) != len(set(columnas)):
        raise ValueError('No repetir nombres de columnas.')
    tabla, metadata = pyreadstat.read_sav(
        ruta, usecols=columnas if parcial else None,
        apply_value_formats=False, user_missing=True,
    )
    faltan = set(columnas) - set(tabla.columns)
    if faltan:
        raise ValueError(f'Columnas ausentes en el SAV: {sorted(faltan)}')
    seleccion = tabla.loc[:, columnas].copy(deep=True)
    relevantes = {}
    for campo in CAMPOS_METADATA:
        diccionario = getattr(metadata, campo)
        relevantes[campo] = {c: diccionario[c] for c in columnas if c in diccionario}
    return seleccion, relevantes


def leer_sav_completo(ruta, columnas):
    """Lee el SAV completo y luego conserva las columnas solicitadas."""
    return _leer(ruta, columnas, parcial=False)


def leer_sav_columnas(ruta, columnas):
    """Lee con usecols y devuelve las columnas en el mismo orden solicitado."""
    return _leer(ruta, columnas, parcial=True)


def verificar_equivalencia(primera, segunda):
    """Exige valores, ausencias, tipos, índice, orden y metadatos iguales."""
    pd.testing.assert_frame_equal(primera[0], segunda[0], check_exact=True)
    if primera[1] != segunda[1]:
        raise AssertionError('Los metadatos de las columnas seleccionadas no coinciden.')


def medir_lecturas(ruta, columnas, repeticiones=5, ejecuciones=1):
    """Verifica equivalencia antes de medir; alterna el orden de las alternativas.

    Cada muestra temporal incluye lectura, selección, copia y extracción de
    metadatos. El máximo de tracemalloc se mide en otra ejecución por alternativa.
    No incluye descarga, hash del archivo, impresión ni escritura de resultados.
    """
    for valor in (repeticiones, ejecuciones):
        if type(valor) is not int or valor < 1:
            raise ValueError('Repeticiones y ejecuciones deben ser enteros positivos.')
    if tracemalloc.is_tracing():
        raise RuntimeError('Detener el rastreo externo de memoria antes de medir.')
    columnas = list(columnas)
    operaciones = {
        'completo_y_seleccion': lambda: leer_sav_completo(ruta, columnas),
        'solo_columnas': lambda: leer_sav_columnas(ruta, columnas),
    }
    # Estas lecturas también calientan la caché; no se presentan tiempos en frío.
    completa = operaciones['completo_y_seleccion']()
    parcial = operaciones['solo_columnas']()
    verificar_equivalencia(completa, parcial)
    filas = len(completa[0])
    del completa, parcial
    muestras = {nombre: [] for nombre in operaciones}
    orden_ejecutado = []
    for repeticion in range(repeticiones):
        orden = list(operaciones)
        if repeticion % 2:
            orden.reverse()
        orden_ejecutado.append(orden)
        for nombre in orden:
            gc.collect()
            total = timeit.Timer(operaciones[nombre]).timeit(number=ejecuciones)
            muestras[nombre].append(total / ejecuciones)
    resultados = {}
    for nombre, operacion in operaciones.items():
        gc.collect()
        tracemalloc.start()
        try:
            tabla, metadata = operacion()
            _, maximo = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        resultados[nombre] = {
            'segundos_por_ejecucion': muestras[nombre],
            'menor_segundos': min(muestras[nombre]),
            'maximo_rastreado_bytes': maximo,
            'tabla_devuelta_bytes': int(tabla.memory_usage(index=True, deep=True).sum()),
        }
        del tabla, metadata
    return {
        'equivalencia': 'OK', 'filas': filas, 'columnas': columnas,
        'metadatos_comparados': list(CAMPOS_METADATA),
        'repeticiones': repeticiones, 'ejecuciones_por_repeticion': ejecuciones,
        'orden_temporal': orden_ejecutado, 'ejecuciones_memoria_por_alternativa': 1,
        'resultados': resultados,
    }
