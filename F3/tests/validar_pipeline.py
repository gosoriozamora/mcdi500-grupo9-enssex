"""Desde la raíz: python F3/tests/validar_pipeline.py. No exporta datos."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'F2/src'))
sys.path.insert(0, str(RAIZ / 'F3/src'))

from pipeline_enssex import PipelineENSSEX
from preparar_enssex import (
    cargar_base, seleccionar_convivientes, limpiar_codigos, tipificar_categorias,
    construir_derivadas, codificar_nominales, validar_resultado,
    disponibilidad_analisis,
)


def esperar_error(tipo, operacion):
    try:
        operacion()
    except tipo:
        return
    raise AssertionError(f'Se esperaba {tipo.__name__}.')


def muestra_controlada(esquema):
    datos = {}
    for variable in esquema['variables']:
        nombre = variable['nombre']
        if variable['categorias']:
            datos[nombre] = [variable['categorias'][0]] * 4
        else:
            datos[nombre] = [2000] * 4
    datos.update({
        'folio_encuesta': [1, 2, 3, 4],
        'fecha': ['01/01/2023'] * 4,
        'p4': [35, 60, 50, 25],
        'p91': [40, 999, 45, 25],
        'p81': [1, 1, 2, 1],
        'p83': [1, 1, 1, 2],
        'p93': [1, 9, 2, 3],
        'i_6_p9': [7, 9, 4, 5],
        'i_2_p9': [6, 9, 4, 5],
        'p3': [1, 9, 1, 1],
    })
    return pd.DataFrame(datos, index=[10, 20, 30, 40])


def comprobar_controlados(esquema):
    base = muestra_controlada(esquema)
    respaldo = base.copy(deep=True)
    reglas = deepcopy(esquema)
    pipeline = PipelineENSSEX(reglas)
    reglas['centrales'].clear()
    resultados = pipeline.ejecutar(base)
    principal = resultados['principal']
    assert principal.shape == (2, 20)
    assert principal.index.tolist() == [10, 20]
    assert principal['folio_encuesta'].tolist() == ['1', '2']
    assert principal.loc[10, 'diferencia_edad_pareja'] == -5
    assert pd.isna(principal.loc[20, 'diferencia_edad_pareja'])
    assert principal.loc[20, esquema['centrales']].isna().all()
    assert resultados['nominales'].shape == (2, 65)
    assert resultados['nominales'].loc[20, 'p3__sin_respuesta'] == 1
    assert resultados['flujo_seleccion']['filas'].tolist() == [4, 3, 2]
    assert resultados['resumen_faltantes']['imputados'].eq(0).all()
    assert resultados['resumen_faltantes']['filas_excluidas'].eq(0).all()
    assert resultados['validaciones']['resultado'].eq('OK').all()
    pd.testing.assert_frame_equal(base, respaldo)

    # Cambiar un resultado no altera otro ni la ejecución siguiente.
    original_tipificada = resultados['tipificada'].copy(deep=True)
    principal.loc[10, 'p4'] = 99
    pd.testing.assert_frame_equal(resultados['tipificada'], original_tipificada)
    assert pipeline.ejecutar(base)['principal'].loc[10, 'p4'] == 35
    unica = pipeline.ejecutar(base.iloc[:1])
    assert unica['principal'].shape == (1, 20)
    assert unica['nominales'].shape == (1, 65)
    todas_ausentes = pipeline.ejecutar(base.iloc[1:2])
    assert todas_ausentes['principal'][esquema['centrales']].isna().all().all()
    print('OK: filtros, categorías, derivada, ausencias y matriz nominal en ejemplos conocidos.')
    print('OK: una persona, centrales ausentes, esquema protegido y ejecuciones independientes.')

    sin_convivientes = base.copy(deep=True)
    sin_convivientes['p83'] = 2
    folios_duplicados = base.copy(deep=True)
    folios_duplicados.loc[20, 'folio_encuesta'] = 1
    codigo_invalido = base.copy(deep=True)
    codigo_invalido.loc[10, 'p93'] = 7
    fecha_invalida = base.copy(deep=True)
    fecha_invalida.loc[10, 'fecha'] = 'fecha desconocida'
    for entrada, error in [
        (None, TypeError), (base.iloc[:0], ValueError),
        (base.drop(columns='p93'), ValueError),
        (pd.concat([base, base[['p93']]], axis=1), ValueError),
        (pd.concat([base, base.iloc[:1]]), ValueError),
        (sin_convivientes, ValueError), (folios_duplicados, ValueError),
        (codigo_invalido, ValueError), (fecha_invalida, ValueError),
    ]:
        esperar_error(error, lambda: pipeline.ejecutar(entrada))
    assert pipeline.ejecutar(base)['principal'].shape == (2, 20)
    pd.testing.assert_frame_equal(base, respaldo)
    print('OK: errores de entrada rechazados y ejecución válida después de los errores.')


def comprobar_reales(esquema):
    evidencia = json.loads((RAIZ / 'docs/datos/verificacion_conversion_enssex.json')
                           .read_text(encoding='utf-8'))
    base = cargar_base(RAIZ / 'data/raw' / evidencia['csv_file'], evidencia, esquema)
    respaldo = base.copy(deep=True)
    resultados = PipelineENSSEX(esquema).ejecutar(base)

    # Referencia construida con las funciones originales de F2, sin clases F3.
    seleccion, flujo = seleccionar_convivientes(base, esquema)
    limpia, resumen = limpiar_codigos(seleccion, esquema)
    tipificada = tipificar_categorias(limpia, esquema)
    final = construir_derivadas(tipificada)
    nominales = codificar_nominales(final, esquema)
    esperados = {
        'seleccion': seleccion, 'limpia': limpia, 'tipificada': tipificada,
        'principal': final, 'nominales': nominales, 'flujo_seleccion': flujo,
        'resumen_limpieza': resumen,
        'disponibilidad': disponibilidad_analisis(limpia, esquema),
        'validaciones': validar_resultado(seleccion, final, nominales, esquema),
    }
    for nombre, esperado in esperados.items():
        pd.testing.assert_frame_equal(resultados[nombre], esperado, check_exact=True)
    assert resultados['principal'].shape == (8579, 20)
    assert resultados['nominales'].shape == (8579, 65)
    assert len(resultados['validaciones']) == 130
    faltantes = resultados['resumen_faltantes']
    assert faltantes['variable'].tolist() == esquema['centrales']
    assert faltantes['imputados'].eq(0).all()
    assert faltantes['filas_excluidas'].eq(0).all()
    assert faltantes['faltantes'].tolist() == limpia[esquema['centrales']].isna().sum().tolist()
    pd.testing.assert_frame_equal(base, respaldo, check_exact=True)
    print('OK: productos e intermedios exactamente equivalentes a F2.')
    print('OK: 8.579 personas, 20 columnas principales y 65 columnas nominales.')
    print('OK: 130 comprobaciones; cero imputaciones y exclusiones por faltantes.')
    print('OK: base de entrada intacta; no se exportaron archivos.')


if __name__ == '__main__':
    esquema = json.loads((RAIZ / 'F2/docs/esquema_variables_F2.json').read_text(encoding='utf-8'))
    comprobar_controlados(esquema)
    comprobar_reales(esquema)
