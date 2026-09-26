"""Desde la raíz: python F3/tests/validar_faltantes.py. No escribe datos."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'F2/src'))
sys.path.insert(0, str(RAIZ / 'F3/src'))

from preparar_enssex import (
    cargar_base, seleccionar_convivientes, limpiar_codigos,
    comparar_imputaciones,
)
from faltantes import (
    TratamientoFaltantes, ESTRATEGIAS, conservar_faltantes,
    casos_disponibles, media_global, mediana_global, mediana_por_dependencia,
)


def esperar_error(tipo, operacion):
    try:
        operacion()
    except tipo:
        return
    raise AssertionError(f'Se esperaba {tipo.__name__}.')


def comprobar_controlados(esquema):
    nombre = 'i_6_p9'
    reducido = deepcopy(esquema)
    reducido['variables'] = [v for v in esquema['variables']
                             if v['nombre'] in (nombre, 'p93')]
    original = pd.DataFrame({
        nombre: [1, 4, 9, None, 9, 9],
        'p93': [1, 1, 1, 1, 9, 2],
    }, index=[10, 20, 30, 40, 50, 60])
    limpia, _ = limpiar_codigos(original, reducido)
    respaldo = limpia.copy(deep=True)
    respaldo_original = original.copy(deep=True)
    esperados = {
        conservar_faltantes: [1, 4, None, None, None, None],
        casos_disponibles: [1, 4],
        media_global: [1, 4, 2.5, None, 2.5, 2.5],
        mediana_global: [1, 4, 2.5, None, 2.5, 2.5],
        mediana_por_dependencia: [1, 4, 2.5, None, None, None],
    }
    for estrategia, valores in esperados.items():
        objeto = TratamientoFaltantes(reducido, nombre, estrategia, original)
        esperar_error(RuntimeError, lambda: objeto.transformar(limpia))
        esperar_error(RuntimeError, objeto.resumen)
        assert objeto.ajustar(limpia) is objeto
        salida = objeto.transformar(limpia)
        indice = original.index[:2] if estrategia is casos_disponibles else original.index
        tipo = 'Int64' if estrategia in (conservar_faltantes, casos_disponibles) else 'Float64'
        esperado = pd.Series(valores, index=indice, name=nombre, dtype=tipo)
        pd.testing.assert_series_equal(salida[nombre], esperado)
        pd.testing.assert_series_equal(salida['p93'], limpia.loc[indice, 'p93'])
        resumen = objeto.resumen().iloc[0]
        assert resumen['elegibles'] == 3
        assert resumen['vacios_originales_protegidos'] == 1
        assert resumen['imputados'] == (3 if estrategia in (media_global, mediana_global)
                                        else 1 if estrategia is mediana_por_dependencia else 0)
        assert resumen['fuera_de_categorias'] == resumen['imputados']
        assert resumen['filas_excluidas'] == (4 if estrategia is casos_disponibles else 0)
        pd.testing.assert_frame_equal(limpia, respaldo)
        pd.testing.assert_frame_equal(original, respaldo_original)
        evidencia = objeto.resumen()
        evidencia.loc[0, 'imputados'] = 999
        assert objeto.resumen().loc[0, 'imputados'] != 999
        salida.iloc[0, 0] = 7
        pd.testing.assert_frame_equal(limpia, respaldo)
        esperar_error(ValueError, lambda: objeto.transformar(limpia.iloc[::-1]))
        esperar_error(RuntimeError, objeto.resumen)
        esperar_error(ValueError, lambda: objeto.ajustar(limpia.drop(columns=nombre)))
        esperar_error(RuntimeError, lambda: objeto.transformar(limpia))
        objeto.ajustar(limpia).transformar(limpia)
    print('OK: cinco estrategias, resultados conocidos, copias y control de estado.')
    print('OK: vacíos originales protegidos; sin grupo o sin donantes no se imputa por grupo.')

    # Cambiar las fuentes externas no cambia las reglas guardadas.
    fuente = original.copy(deep=True)
    reglas = deepcopy(reducido)
    objeto = TratamientoFaltantes(reglas, nombre, mediana_global, fuente)
    fuente.loc[30, nombre] = 1
    reglas['variables'] = []
    assert objeto.ajustar(limpia).transformar(limpia).loc[30, nombre] == 2.5

    for valores in ([1], [1, 4], [9, None]):
        raw = pd.DataFrame({nombre: valores, 'p93': [1] * len(valores)})
        tabla, _ = limpiar_codigos(raw, reducido)
        for estrategia in ESTRATEGIAS:
            obj = TratamientoFaltantes(reducido, nombre, estrategia, raw).ajustar(tabla)
            salida = obj.transformar(tabla)
            if valores == [9, None]:
                assert salida[nombre].isna().all()
                assert obj.resumen().loc[0, 'imputados'] == 0
                assert pd.isna(obj.resumen().loc[0, 'cambio_varianza_pct'])
            elif estrategia is conservar_faltantes:
                pd.testing.assert_frame_equal(salida, tabla)

    esperar_error(ValueError, lambda: TratamientoFaltantes(
        esquema, 'p93', mediana_por_dependencia, original))
    esperar_error(ValueError, lambda: TratamientoFaltantes(
        esquema, 'p1', media_global, original))
    esperar_error(ValueError, lambda: TratamientoFaltantes(
        esquema, nombre, lambda s, e, g: s, original))
    obj = TratamientoFaltantes(esquema, nombre, media_global, original)
    alterada = limpia.copy(deep=True)
    alterada.loc[10, nombre] = 7
    for tabla, error in [(alterada, ValueError), (limpia.iloc[:0], ValueError),
                         ([1, 2], TypeError),
                         (pd.concat([limpia, limpia[[nombre]]], axis=1), ValueError)]:
        esperar_error(error, lambda: obj.ajustar(tabla))
    print('OK: límites, configuración protegida y rechazo de entradas no correspondientes.')


def comprobar_reales(esquema):
    evidencia = json.loads((RAIZ / 'docs/datos/verificacion_conversion_enssex.json')
                           .read_text(encoding='utf-8'))
    base = cargar_base(RAIZ / 'data/raw' / evidencia['csv_file'], evidencia, esquema)
    original, _ = seleccionar_convivientes(base, esquema)
    limpia, _ = limpiar_codigos(original, esquema)
    respaldo = limpia.copy(deep=True)
    respaldo_original = original.copy(deep=True)
    referencia = comparar_imputaciones(limpia, esquema['centrales'])
    filas = []
    for nombre in esquema['centrales']:
        # En estos datos las tres centrales no tienen vacíos originales.
        # Por eso la restricción de elegibilidad debe reproducir F2 exactamente.
        assert original[nombre].notna().all()
        for estrategia in ESTRATEGIAS:
            if nombre == 'p93' and estrategia is mediana_por_dependencia:
                continue
            objeto = TratamientoFaltantes(esquema, nombre, estrategia, original)
            salida = objeto.ajustar(limpia).transformar(limpia)
            s = limpia[nombre].astype('Float64')
            if estrategia is conservar_faltantes:
                esperada = s
                pd.testing.assert_frame_equal(salida, limpia)
            elif estrategia is casos_disponibles:
                esperada = s.dropna()
            elif estrategia is media_global:
                esperada = s.fillna(s.mean())
            elif estrategia is mediana_global:
                esperada = s.fillna(s.median())
            else:
                esperada = s.fillna(s.groupby(limpia['p93']).transform('median'))
            pd.testing.assert_series_equal(salida[nombre].astype('Float64'), esperada)
            otras = limpia.columns.drop(nombre)
            pd.testing.assert_frame_equal(salida[otras], limpia.loc[salida.index, otras])
            filas.append(objeto.resumen())
    obtenido = pd.concat(filas, ignore_index=True)
    pd.testing.assert_frame_equal(obtenido[referencia.columns], referencia)
    pd.testing.assert_frame_equal(limpia, respaldo)
    pd.testing.assert_frame_equal(original, respaldo_original)
    assert limpia.shape == (8579, 19)
    print('OK: 14 escenarios equivalentes a F2 en valores y resumen; 8.579 personas y 19 columnas.')
    print('OK: conservar faltantes mantiene tabla, tipos e índice; ninguna entrada fue modificada.')
    print('Alcance: escenarios descriptivos; no se generan ni reemplazan productos de datos.')


if __name__ == '__main__':
    esquema = json.loads((RAIZ / 'F2/docs/esquema_variables_F2.json').read_text(encoding='utf-8'))
    comprobar_controlados(esquema)
    comprobar_reales(esquema)
