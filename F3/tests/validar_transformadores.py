"""Pruebas de limpieza y tipificación de categorías de F3.

Desde la raíz del repositorio:
python F3/tests/validar_transformadores.py

Las pruebas no generan ni reemplazan archivos de datos.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pandas as pd


def esperar_error(tipo, operacion):
    """Comprueba que una operación produzca la excepción esperada."""
    try:
        operacion()
    except tipo:
        return
    raise AssertionError(f"Se esperaba {tipo.__name__}.")


def verificar_casos_controlados(esquema):
    from transformadores import LimpiadorCodigos, Transformador

    especificacion = next(
        v for v in esquema["variables"] if v["nombre"] == "p93"
    )
    reducido = {"variables": [deepcopy(especificacion)]}

    entrada = pd.DataFrame(
        {"p93": [1, 9, None, 3]},
        index=[10, 20, 30, 40],
    )
    original = entrada.copy(deep=True)
    esperado = pd.DataFrame(
        {"p93": pd.array([1, None, None, 3], dtype="Int64")},
        index=entrada.index,
    )

    limpiador = LimpiadorCodigos(reducido)
    casos = []

    esperar_error(
        RuntimeError,
        lambda: limpiador.transformar(entrada),
    )
    esperar_error(RuntimeError, limpiador.resumen)
    casos.append(
        "Impide transformar o consultar resultados antes de tiempo"
    )

    limpiador.ajustar(entrada)
    resultado = limpiador.transformar(entrada)

    pd.testing.assert_frame_equal(resultado, esperado)
    pd.testing.assert_frame_equal(entrada, original)

    resumen = limpiador.resumen()
    assert resumen.loc[0, "NS_NR_a_faltante"] == 1
    assert resumen.loc[0, "faltantes_despues"] == 2
    casos.append(
        "Caso normal: códigos, ausencias, tipos e índice correctos"
    )

    resultado.loc[10, "p93"] = 2
    resumen.loc[0, "NS_NR_a_faltante"] = 999

    pd.testing.assert_frame_equal(entrada, original)
    assert limpiador.resumen().loc[0, "NS_NR_a_faltante"] == 1
    casos.append(
        "Las copias protegen la entrada y el resumen interno"
    )

    reducido["variables"][0]["no_respuesta"] = []
    pd.testing.assert_frame_equal(
        limpiador.transformar(entrada),
        esperado,
    )
    casos.append(
        "Cambiar el esquema externo no altera las reglas del objeto"
    )

    for valores in ([2], [1, 2, 3], [9, None]):
        muestra = pd.DataFrame({"p93": valores})
        salida = limpiador.transformar(muestra)

        assert len(salida) == len(muestra)

        if valores == [9, None]:
            assert salida["p93"].isna().all()
        else:
            pd.testing.assert_series_equal(
                salida["p93"],
                muestra["p93"].astype("Int64"),
            )

    casos.append(
        "Límites: una fila, sin faltantes y todos faltantes"
    )

    for muestra, tipo in [
        (pd.DataFrame({"otra": [1]}), ValueError),
        (pd.DataFrame({"p93": []}), ValueError),
        (
            pd.DataFrame([[1, 2]], columns=["p93", "p93"]),
            ValueError,
        ),
        ([1, 2], TypeError),
        (pd.DataFrame({"p93": [7]}), ValueError),
        (pd.DataFrame({"p93": ["texto"]}), ValueError),
    ]:
        esperar_error(
            tipo,
            lambda: limpiador.transformar(muestra),
        )
        esperar_error(RuntimeError, limpiador.resumen)

    casos.append(
        "Rechaza columnas ausentes o duplicadas, vacío, tipo y código inválidos"
    )

    esperar_error(
        ValueError,
        lambda: limpiador.ajustar(pd.DataFrame({"otra": [1]})),
    )
    esperar_error(
        RuntimeError,
        lambda: limpiador.transformar(entrada),
    )

    limpiador.ajustar(entrada)
    pd.testing.assert_frame_equal(
        limpiador.transformar(entrada),
        esperado,
    )
    casos.append(
        "Un ajuste fallido deshabilita el objeto; un ajuste válido permite recuperarlo"
    )

    base = Transformador(["p93"]).ajustar(entrada)
    esperar_error(
        NotImplementedError,
        lambda: base.transformar(entrada),
    )
    casos.append(
        "La clase base exige que la clase hija aporte la operación"
    )

    return casos


def verificar_datos_reales(raiz, esquema):
    from preparar_enssex import (
        cargar_base,
        seleccionar_convivientes,
        limpiar_codigos,
        tipificar_categorias,
    )
    from transformadores import LimpiadorCodigos, TipificadorCategorias

    ruta_evidencia = (
        raiz / "docs/datos/verificacion_conversion_enssex.json"
    )
    evidencia = json.loads(
        ruta_evidencia.read_text(encoding="utf-8")
    )

    base = cargar_base(
        raiz / "data/raw" / evidencia["csv_file"],
        evidencia,
        esquema,
    )
    seleccion, _ = seleccionar_convivientes(base, esquema)
    original = seleccion.copy(deep=True)

    esperado, resumen_esperado = limpiar_codigos(
        seleccion,
        esquema,
    )

    limpiador = LimpiadorCodigos(esquema).ajustar(seleccion)
    resultado = limpiador.transformar(seleccion)

    pd.testing.assert_frame_equal(resultado, esperado)
    pd.testing.assert_frame_equal(
        limpiador.resumen(),
        resumen_esperado,
    )
    pd.testing.assert_frame_equal(seleccion, original)

    assert resultado.shape == (8579, 19)

    print(
        f"OK: selección real de {len(resultado):,} personas "
        f"y {len(resultado.columns)} columnas."
    )
    print(
        "OK: valores, ausencias, tipos, orden y resumen "
        "idénticos a la limpieza de F2."
    )

    # Comparamos la nueva clase con la tipificación original de F2.
    limpia_original = resultado.copy(deep=True)
    categorias_esperadas = tipificar_categorias(esperado, esquema)
    tipificador = TipificadorCategorias(esquema).ajustar(resultado)
    tipificada = tipificador.transformar(resultado)

    pd.testing.assert_frame_equal(tipificada, categorias_esperadas)
    pd.testing.assert_frame_equal(resultado, limpia_original)
    pd.testing.assert_frame_equal(seleccion, original)
    pd.testing.assert_frame_equal(
        tipificada.isna(),
        limpia_original.isna(),
    )
    assert tipificada.shape == (8579, 19)

    # Además de comparar con F2, comprobamos el esquema y los códigos.
    for variable in esquema["variables"]:
        nombre = variable["nombre"]
        categorias = variable["categorias"]
        if categorias:
            assert tipificada[nombre].cat.categories.tolist() == categorias
            assert tipificada[nombre].cat.ordered == variable["ordenada"]
            pd.testing.assert_series_equal(
                tipificada[nombre].astype(limpia_original[nombre].dtype),
                limpia_original[nombre],
            )
        else:
            pd.testing.assert_series_equal(
                tipificada[nombre],
                limpia_original[nombre],
            )

    print(
        "OK: tipificación real de 8.579 personas y 19 columnas "
        "idéntica a F2."
    )
    print(
        "OK: categorías y orden coinciden con el esquema; "
        "códigos, faltantes y columnas no categóricas conservados."
    )
    print(
        "OK: entradas de limpieza y tipificación intactas. "
        "Esta prueba no genera "
        "ni reemplaza archivos de datos."
    )
    print(
        "Alcance: limpieza y tipificación verificadas sobre ENSSEX real; "
        "todavía no es el pipeline completo de F3."
    )


def verificar_categorias():
    from transformadores import TipificadorCategorias

    # Ejemplo pequeño: una variable ordenada y otra sin orden.
    esquema = {
        "variables": [
            {
                "nombre": "nivel",
                "categorias": [1, 2, 3],
                "ordenada": True,
            },
            {
                "nombre": "grupo",
                "categorias": [10, 20],
                "ordenada": False,
            },
        ]
    }

    entrada = pd.DataFrame({
        "nivel": [2, None, 1],
        "grupo": [20, 10, None],
    })
    original = entrada.copy(deep=True)
    tipificador = TipificadorCategorias(esquema)

    esperar_error(
        RuntimeError,
        lambda: tipificador.transformar(entrada),
    )

    tipificador.ajustar(entrada)
    resultado = tipificador.transformar(entrada)

    esperado = pd.DataFrame({
        "nivel": pd.Categorical(
            [2, None, 1],
            categories=[1, 2, 3],
            ordered=True,
        ),
        "grupo": pd.Categorical(
            [20, 10, None],
            categories=[10, 20],
            ordered=False,
        ),
    })

    pd.testing.assert_frame_equal(resultado, esperado)
    pd.testing.assert_frame_equal(entrada, original)

    # Una categoría desconocida debe generar un error.
    invalida = entrada.copy(deep=True)
    invalida.loc[0, "nivel"] = 7

    esperar_error(
        ValueError,
        lambda: tipificador.transformar(invalida),
    )

    print("OK: categorías ordinales y nominales correctas.")
    print("OK: valores, faltantes y entrada conservados.")
    print(
        "OK: rechaza categorías desconocidas "
        "y uso antes de ajustar."
    )


def main():
    raiz = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(raiz / "F2/src"))
    sys.path.insert(0, str(raiz / "F3/src"))

    esquema = json.loads(
        (raiz / "F2/docs/esquema_variables_F2.json").read_text(
            encoding="utf-8"
        )
    )

    for caso in verificar_casos_controlados(esquema):
        print("OK:", caso)

    verificar_categorias()
    verificar_datos_reales(raiz, esquema)


if __name__ == "__main__":
    main()
