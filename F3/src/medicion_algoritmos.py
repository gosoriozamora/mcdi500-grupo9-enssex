"""Mide alternativas equivalentes sobre muestras de rendimiento, no personas nuevas."""
import gc
import timeit
import tracemalloc

import pandas as pd

from diferencia_edad import validar_edades, diferencia_con_bucle, diferencia_por_columnas


def validar_configuracion(tamanos, repeticiones, ejecuciones, semilla):
    """Exige tamaños crecientes y parámetros reproducibles antes de medir."""
    if not isinstance(tamanos, (list, tuple)) or not tamanos:
        raise ValueError('Indicar una lista o tupla no vacía de tamaños.')
    if any(type(n) is not int or n < 1 for n in tamanos):
        raise ValueError('Los tamaños deben ser enteros positivos.')
    if list(tamanos) != sorted(set(tamanos)):
        raise ValueError('Los tamaños deben ser distintos y crecientes.')
    for valor in (repeticiones, ejecuciones):
        if type(valor) is not int or valor < 1:
            raise ValueError('Repeticiones y ejecuciones deben ser enteros positivos.')
    if type(semilla) is not int or not 0 <= semilla < 2**32:
        raise ValueError('La semilla debe ser un entero entre 0 y 2**32 - 1.')


def crear_muestra(edades, filas, semilla):
    """Muestreo con reemplazo; el índice nuevo evita medir índices de distinto tamaño."""
    return edades.sample(n=filas, replace=True, random_state=semilla).reset_index(drop=True)


def medir_alternativas(tabla, tamanos=(1000, 5000, 20000, 50000),
                       repeticiones=5, ejecuciones=5, semilla=42):
    """Verifica cada muestra antes de medir tiempo y, por separado, memoria.

    El intervalo temporal incluye la validación compartida y la construcción de
    la serie; excluye preparar muestras, comparar resultados y guardar evidencia.
    """
    validar_configuracion(tamanos, repeticiones, ejecuciones, semilla)
    validar_edades(tabla)
    if tabla.empty:
        raise ValueError('Se necesitan edades de entrada para generar muestras.')
    if tracemalloc.is_tracing():
        raise RuntimeError('Detener el rastreo externo de memoria antes de medir.')
    edades = tabla[['p4', 'p91']].copy(deep=True)
    operaciones = {'bucle': diferencia_con_bucle, 'columnas': diferencia_por_columnas}
    mediciones = []
    for filas in tamanos:
        muestra = crear_muestra(edades, filas, semilla)
        respaldo = muestra.copy(deep=True)
        bucle = diferencia_con_bucle(muestra)
        columnas = diferencia_por_columnas(muestra)
        pd.testing.assert_series_equal(bucle, columnas, check_exact=True)
        faltantes = int(bucle.isna().sum())
        del bucle, columnas
        tiempos = {nombre: [] for nombre in operaciones}
        orden_temporal = []
        for repeticion in range(repeticiones):
            orden = list(operaciones)
            if repeticion % 2:
                orden.reverse()
            orden_temporal.append(orden)
            for nombre in orden:
                gc.collect()
                operacion = operaciones[nombre]
                total = timeit.Timer(lambda: operacion(muestra)).timeit(number=ejecuciones)
                tiempos[nombre].append(total / ejecuciones)
        resultados = {}
        for nombre, operacion in operaciones.items():
            gc.collect()
            tracemalloc.start()
            try:
                serie = operacion(muestra)
                _, maximo = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
            resultados[nombre] = {
                'segundos_por_ejecucion': tiempos[nombre],
                'menor_segundos': min(tiempos[nombre]),
                'maximo_rastreado_bytes': maximo,
                'serie_devuelta_bytes': int(serie.memory_usage(index=True, deep=True)),
            }
            del serie
        pd.testing.assert_frame_equal(muestra, respaldo, check_exact=True)
        mediciones.append({
            'filas': filas, 'equivalencia': 'OK', 'entrada_intacta': True,
            'diferencias_ausentes': faltantes, 'orden_temporal': orden_temporal,
            'resultados': resultados,
        })
    return {
        'filas_fuente': len(edades), 'tamanos': list(tamanos), 'semilla': semilla,
        'muestreo': 'Con reemplazo, solo p4 y p91; índice reiniciado en cada muestra.',
        'repeticiones': repeticiones, 'ejecuciones_por_repeticion': ejecuciones,
        'ejecuciones_memoria_por_alternativa_y_tamano': 1,
        'mediciones': mediciones,
    }
