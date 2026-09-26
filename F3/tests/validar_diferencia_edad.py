"""Desde la raíz: python F3/tests/validar_diferencia_edad.py. No exporta datos."""
import json
from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'F2/src'))
sys.path.insert(0, str(RAIZ / 'F3/src'))

from diferencia_edad import diferencia_con_bucle, diferencia_por_columnas
from preparar_enssex import (
    cargar_base, seleccionar_convivientes, limpiar_codigos, construir_derivadas,
)

ALTERNATIVAS = (diferencia_con_bucle, diferencia_por_columnas)


def esperar_error(tipo, operacion):
    try:
        operacion()
    except tipo:
        return
    raise AssertionError(f'Se esperaba {tipo.__name__}.')


def comprobar_resultados(tabla, esperado):
    respaldo = tabla.copy(deep=True)
    for alternativa in ALTERNATIVAS:
        obtenido = alternativa(tabla)
        pd.testing.assert_series_equal(obtenido, esperado, check_exact=True)
        pd.testing.assert_frame_equal(tabla, respaldo, check_exact=True)
        if len(obtenido):
            obtenido.iloc[0] = 999
            pd.testing.assert_frame_equal(tabla, respaldo, check_exact=True)


def comprobar_controlados():
    # Índice desordenado y repetido: el cálculo conserva posiciones y etiquetas.
    tabla = pd.DataFrame({
        'p4': pd.array([35, 60, 25, None, 45, None, 120], dtype='Int64'),
        'p91': pd.array([40, 45, 25, 30, None, None, 18], dtype='Int64'),
    }, index=pd.Index([8, 2, 8, 1, 9, 4, 0], name='fila'))
    esperado = pd.Series([-5, 15, 0, pd.NA, pd.NA, pd.NA, 102],
                         index=tabla.index, dtype='Int64', name='diferencia_edad_pareja')
    comprobar_resultados(tabla, esperado)
    for posiciones in ([], [0], [0, 1, 2], [3, 4, 5]):
        comprobar_resultados(tabla.iloc[posiciones], esperado.iloc[posiciones])
    print('OK: diferencias conocidas, signo, cero, faltantes, índice y tipo Int64.')
    print('OK: vacío, una fila, sin faltantes, todos faltantes y copias independientes.')

    for alternativa in ALTERNATIVAS:
        esperar_error(TypeError, lambda: alternativa([35, 40]))
        esperar_error(ValueError, lambda: alternativa(tabla.drop(columns='p91')))
        duplicada = pd.concat([tabla, tabla[['p4']]], axis=1)
        esperar_error(ValueError, lambda: alternativa(duplicada))
        for tipo in ('Float64', 'string'):
            invalida = tabla.copy(deep=True)
            invalida['p4'] = invalida['p4'].astype(tipo)
            esperar_error(TypeError, lambda: alternativa(invalida))
    print('OK: rechaza estructura o tipos incorrectos; exige edades previamente limpias.')


def comprobar_reales():
    esquema = json.loads((RAIZ / 'F2/docs/esquema_variables_F2.json').read_text(encoding='utf-8'))
    evidencia = json.loads((RAIZ / 'docs/datos/verificacion_conversion_enssex.json')
                           .read_text(encoding='utf-8'))
    base = cargar_base(RAIZ / 'data/raw' / evidencia['csv_file'], evidencia, esquema)
    seleccion, _ = seleccionar_convivientes(base, esquema)
    limpia, _ = limpiar_codigos(seleccion, esquema)
    esperado = construir_derivadas(limpia)['diferencia_edad_pareja']
    assert len(esperado) == 8579
    comprobar_resultados(limpia, esperado)
    print('OK: ambas alternativas coinciden exactamente con F2 para 8.579 personas.')
    print('OK: valores, faltantes, nombre, tipo e índice conservados; entrada intacta.')
    print('Alcance: equivalencia de algoritmos; tiempos y memoria se medirán por separado.')


if __name__ == '__main__':
    comprobar_controlados()
    comprobar_reales()
