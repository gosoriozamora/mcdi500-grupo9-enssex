"""Pruebas pequeñas de medición; no exigen que una alternativa sea más rápida."""
from pathlib import Path
import sys
import tracemalloc
from unittest.mock import patch

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'F3/src'))

from diferencia_edad import diferencia_por_columnas
from medicion_algoritmos import crear_muestra, medir_alternativas


def esperar_error(tipo, operacion):
    try:
        operacion()
    except tipo:
        return
    raise AssertionError(f'Se esperaba {tipo.__name__}.')


def comprobar():
    edades = pd.DataFrame({
        'p4': pd.array([35, None, 25, 90], dtype='Int64'),
        'p91': pd.array([40, 22, None, 18], dtype='Int64'),
    }, index=[5, 1, 5, 3])
    respaldo = edades.copy(deep=True)
    primera = crear_muestra(edades, 20, 42)
    pd.testing.assert_frame_equal(primera, crear_muestra(edades, 20, 42))
    assert primera.index.equals(pd.RangeIndex(20))
    assert len(primera) > len(edades)
    for nombre in edades:
        assert primera[nombre].dropna().isin(edades[nombre].dropna()).all()
    print('OK: muestras reproducibles con reemplazo; no amplían la población del estudio.')

    resultado = medir_alternativas(edades, [1, 8], repeticiones=2, ejecuciones=2)
    for medicion in resultado['mediciones']:
        assert medicion['equivalencia'] == 'OK'
        assert medicion['entrada_intacta']
        assert medicion['orden_temporal'] == [['bucle', 'columnas'], ['columnas', 'bucle']]
        muestra = crear_muestra(edades, medicion['filas'], 42)
        serie = diferencia_por_columnas(muestra)
        assert medicion['diferencias_ausentes'] == int(serie.isna().sum())
        for valores in medicion['resultados'].values():
            tiempos = valores['segundos_por_ejecucion']
            assert len(tiempos) == 2 and all(t >= 0 for t in tiempos)
            assert valores['menor_segundos'] == min(tiempos)
            assert valores['maximo_rastreado_bytes'] > 0
            assert valores['serie_devuelta_bytes'] == int(serie.memory_usage(index=True, deep=True))
    pd.testing.assert_frame_equal(edades, respaldo, check_exact=True)
    print('OK: repeticiones, orden alternado, faltantes y dos métricas de memoria por tamaño.')

    # Un resultado alterado debe detener la comparación antes de cronometrar.
    with patch('medicion_algoritmos.diferencia_con_bucle',
               side_effect=lambda tabla: diferencia_por_columnas(tabla).rename('incorrecto')):
        with patch('medicion_algoritmos.timeit.Timer') as cronometro:
            esperar_error(AssertionError, lambda: medir_alternativas(edades, [2], 1, 1))
            cronometro.assert_not_called()
    print('OK: una diferencia entre alternativas impide iniciar las mediciones.')

    for tamanos in ([], [0], [-1], [True], [1.5], [2, 1], [2, 2], '1000'):
        esperar_error(ValueError, lambda: medir_alternativas(edades, tamanos))
    for valor in (0, -1, 1.5, True):
        esperar_error(ValueError, lambda: medir_alternativas(edades, [1], repeticiones=valor))
        esperar_error(ValueError, lambda: medir_alternativas(edades, [1], ejecuciones=valor))
    for semilla in (-1, 2**32, True, 1.5):
        esperar_error(ValueError, lambda: medir_alternativas(edades, [1], semilla=semilla))
    esperar_error(ValueError, lambda: medir_alternativas(edades.iloc[:0], [1]))
    esperar_error(TypeError, lambda: medir_alternativas(edades.astype('Float64'), [1]))
    tracemalloc.start()
    try:
        esperar_error(RuntimeError, lambda: medir_alternativas(edades, [1]))
        assert tracemalloc.is_tracing()
    finally:
        tracemalloc.stop()
    print('OK: configuración inválida rechazada; rastreo externo protegido; entrada intacta.')


if __name__ == '__main__':
    comprobar()
