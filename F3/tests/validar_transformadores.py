"""Pruebas del primer componente de F3, sin escribir productos de datos.

Desde la raíz del repositorio: python F3/tests/validar_transformadores.py
La raíz se obtiene de la ubicación del script, sin rutas particulares del equipo.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pandas as pd


def esperar_error(tipo, operacion):
    """Comprueba que una entrada incorrecta produzca la excepción esperada."""
    try:
        operacion()
    except tipo:
        return
    raise AssertionError(f"Se esperaba {tipo.__name__}.")


def verificar_casos_controlados(esquema):
    from transformadores import LimpiadorCodigos, Transformador

    especificacion = next(v for v in esquema["variables"] if v["nombre"] == "p93")
    reducido = {"variables": [deepcopy(especificacion)]}
    entrada = pd.DataFrame({"p93": [1, 9, None, 3]}, index=[10, 20, 30, 40])
    original = entrada.copy(deep=True)
    esperado = pd.DataFrame({"p93": pd.array([1, None, None, 3], dtype="Int64")},
                            index=entrada.index)
    limpiador = LimpiadorCodigos(reducido)
    casos = []

    esperar_error(RuntimeError, lambda: limpiador.transformar(entrada))
    esperar_error(RuntimeError, limpiador.resumen)
    casos.append("Impide transformar o consultar resultados antes de tiempo")

    limpiador.ajustar(entrada)
    resultado = limpiador.transformar(entrada)
    pd.testing.assert_frame_equal(resultado, esperado)
    pd.testing.assert_frame_equal(entrada, original)
    resumen = limpiador.resumen()
    assert resumen.loc[0, "NS_NR_a_faltante"] == 1
    assert resumen.loc[0, "faltantes_despues"] == 2
    casos.append("Caso normal: códigos, ausencias, tipos e índice correctos")

    resultado.loc[10, "p93"] = 2
    resumen.loc[0, "NS_NR_a_faltante"] = 999
    pd.testing.assert_frame_equal(entrada, original)
    assert limpiador.resumen().loc[0, "NS_NR_a_faltante"] == 1
    casos.append("Las copias protegen la entrada y el resumen interno")

    reducido["variables"][0]["no_respuesta"] = []
    pd.testing.assert_frame_equal(limpiador.transformar(entrada), esperado)
    casos.append("Cambiar el esquema externo no altera las reglas del objeto")

    for valores in ([2], [1, 2, 3], [9, None]):
        muestra = pd.DataFrame({"p93": valores})
        salida = limpiador.transformar(muestra)
        assert len(salida) == len(muestra)
        if valores == [9, None]:
            assert salida["p93"].isna().all()
        else:
            pd.testing.assert_series_equal(salida["p93"], muestra["p93"].astype("Int64"))
    casos.append("Límites: una fila, sin faltantes y todos faltantes")

    for muestra, tipo in [
        (pd.DataFrame({"otra": [1]}), ValueError),
        (pd.DataFrame({"p93": []}), ValueError),
        (pd.DataFrame([[1, 2]], columns=["p93", "p93"]), ValueError),
        ([1, 2], TypeError),
        (pd.DataFrame({"p93": [7]}), ValueError),
        (pd.DataFrame({"p93": ["texto"]}), ValueError),
    ]:
        esperar_error(tipo, lambda: limpiador.transformar(muestra))
        esperar_error(RuntimeError, limpiador.resumen)
    casos.append("Rechaza columnas ausentes o duplicadas, vacío, tipo y código inválidos")

    esperar_error(ValueError, lambda: limpiador.ajustar(pd.DataFrame({"otra": [1]})))
    esperar_error(RuntimeError, lambda: limpiador.transformar(entrada))
    limpiador.ajustar(entrada)
    pd.testing.assert_frame_equal(limpiador.transformar(entrada), esperado)
    casos.append("Un ajuste fallido deshabilita el objeto; un ajuste válido permite recuperarlo")

    base = Transformador(["p93"]).ajustar(entrada)
    esperar_error(NotImplementedError, lambda: base.transformar(entrada))
    casos.append("La clase base exige que la clase hija aporte la operación")
    return casos


def verificar_datos_reales(raiz, esquema):
    from preparar_enssex import cargar_base, seleccionar_convivientes, limpiar_codigos
    from transformadores import LimpiadorCodigos

    evidencia = json.loads((raiz / "docs/datos/verificacion_conversion_enssex.json").read_text(encoding="utf-8"))
    base = cargar_base(raiz / "data/raw" / evidencia["csv_file"], evidencia, esquema)
    seleccion, _ = seleccionar_convivientes(base, esquema)
    original = seleccion.copy(deep=True)
    esperado, resumen_esperado = limpiar_codigos(seleccion, esquema)
    limpiador = LimpiadorCodigos(esquema).ajustar(seleccion)
    resultado = limpiador.transformar(seleccion)
    pd.testing.assert_frame_equal(resultado, esperado)
    pd.testing.assert_frame_equal(limpiador.resumen(), resumen_esperado)
    pd.testing.assert_frame_equal(seleccion, original)
    assert resultado.shape == (8579, 19)
    print(f"OK: selección real de {len(resultado):,} personas y {len(resultado.columns)} columnas.")
    print("OK: valores, ausencias, tipos, orden y resumen idénticos a la limpieza de F2.")
    print("OK: entrada intacta. Esta prueba no genera ni reemplaza archivos de datos.")
    print("Alcance: primer paso de limpieza; todavía no es el pipeline completo de F3.")


def main():
    raiz = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(raiz / "F2/src"))
    sys.path.insert(0, str(raiz / "F3/src"))
    esquema = json.loads((raiz / "F2/docs/esquema_variables_F2.json").read_text(encoding="utf-8"))
    for caso in verificar_casos_controlados(esquema):
        print("OK:", caso)
    verificar_datos_reales(raiz, esquema)


if __name__ == "__main__":
    main()
