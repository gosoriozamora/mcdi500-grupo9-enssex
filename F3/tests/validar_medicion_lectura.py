"""Pruebas de lectura y medición con un SAV pequeño en una carpeta temporal."""
from copy import deepcopy
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import tracemalloc

import pandas as pd
import pyreadstat

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'F2/src'))
sys.path.insert(0, str(RAIZ / 'F3/src'))

from preparar_enssex import sha256_archivo
from medicion_lectura import (
    leer_sav_completo, leer_sav_columnas, verificar_equivalencia, medir_lecturas,
)
from validar_pipeline import esperar_error


def comprobar(carpeta):
    ruta = carpeta / 'ejemplo.sav'
    original = pd.DataFrame({
        'folio': ['001', '002', '003'], 'codigo': [1., 9., float('nan')],
        'extra': [5., 6., 7.],
    })
    pyreadstat.write_sav(
        original, ruta, column_labels={'codigo': 'Categoría de ejemplo'},
        variable_value_labels={'codigo': {1.: 'Sí', 9.: 'Sin respuesta'}},
        missing_ranges={'codigo': [9.]}, variable_measure={'codigo': 'ordinal'},
    )
    identidad = sha256_archivo(ruta)
    columnas = ['codigo', 'folio']  # Orden distinto del almacenado en el SAV.
    completa = leer_sav_completo(ruta, columnas)
    parcial = leer_sav_columnas(ruta, columnas)
    verificar_equivalencia(completa, parcial)
    assert parcial[0].columns.tolist() == columnas
    assert parcial[0]['folio'].tolist() == ['001', '002', '003']
    assert parcial[0]['codigo'].iloc[1] == 9  # No convertir faltante SPSS automáticamente.
    assert pd.isna(parcial[0]['codigo'].iloc[2])
    assert parcial[1]['column_names_to_labels']['codigo'] == 'Categoría de ejemplo'
    assert parcial[1]['variable_measure']['codigo'] == 'ordinal'
    assert parcial[1]['variable_value_labels']['codigo'][9.] == 'Sin respuesta'
    assert parcial[1]['missing_ranges']['codigo'] == [{'lo': 9., 'hi': 9.}]
    alterada = parcial[0].copy(deep=True)
    alterada.loc[0, 'codigo'] = 2
    esperar_error(AssertionError, lambda: verificar_equivalencia(completa, (alterada, parcial[1])))
    etiquetas = deepcopy(parcial[1])
    etiquetas['column_names_to_labels']['codigo'] = 'Otra etiqueta'
    esperar_error(AssertionError, lambda: verificar_equivalencia(completa, (parcial[0], etiquetas)))
    print('OK: valores, tipos, orden solicitado, texto, ausencias y metadatos equivalentes.')
    print('OK: códigos de faltantes SPSS conservados; detecta valores o etiquetas distintos.')

    for operacion in (leer_sav_completo, leer_sav_columnas):
        for solicitud in ([], ['folio', 'folio'], [5], ['inexistente']):
            esperar_error(ValueError, lambda: operacion(ruta, solicitud))
    for valor in (0, -1, 1.5, True):
        esperar_error(ValueError, lambda: medir_lecturas(ruta, columnas, repeticiones=valor))
        esperar_error(ValueError, lambda: medir_lecturas(ruta, columnas, ejecuciones=valor))
    tracemalloc.start()
    try:
        esperar_error(RuntimeError, lambda: medir_lecturas(ruta, columnas))
        assert tracemalloc.is_tracing()
    finally:
        tracemalloc.stop()
    medicion = medir_lecturas(ruta, columnas, repeticiones=2, ejecuciones=2)
    assert medicion['equivalencia'] == 'OK'
    assert medicion['filas'] == 3
    assert medicion['orden_temporal'][1] == medicion['orden_temporal'][0][::-1]
    for valores in medicion['resultados'].values():
        assert len(valores['segundos_por_ejecucion']) == 2
        assert all(t >= 0 for t in valores['segundos_por_ejecucion'])
        assert valores['menor_segundos'] == min(valores['segundos_por_ejecucion'])
        assert valores['maximo_rastreado_bytes'] > 0
        assert valores['tabla_devuelta_bytes'] == int(parcial[0].memory_usage(index=True, deep=True).sum())
    assert not tracemalloc.is_tracing()
    assert sha256_archivo(ruta) == identidad
    print('OK: configuración inválida rechazada; no interfiere con rastreo externo de memoria.')
    print('OK: repeticiones registradas, orden alternado y dos métricas de memoria separadas.')
    print('OK: SAV de prueba intacto; no se exige que una alternativa gane en cada equipo.')


if __name__ == '__main__':
    with TemporaryDirectory() as carpeta:
        comprobar(Path(carpeta))
