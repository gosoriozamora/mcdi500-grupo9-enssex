"""Primeros transformadores de F3: reutilizamos las reglas comprobadas de F2.

El entorno de ejecución debe incluir F2/src en su ruta de importación.
"""
from copy import deepcopy

import pandas as pd
from preparar_enssex import limpiar_codigos, validar_columnas


class Transformador:
    """Contrato común: validar, ajustar y transformar sin modificar la entrada."""

    def __init__(self, columnas):
        self._columnas = tuple(columnas)
        self._ajustado = False

    def _validar_entrada(self, tabla):
        if not isinstance(tabla, pd.DataFrame):
            raise TypeError("La entrada debe ser un DataFrame de pandas.")
        validar_columnas(tabla, self._columnas)

    def ajustar(self, tabla):
        """Comprueba la entrada y habilita el uso de transformar().

        Las reglas de este primer componente proceden del esquema de F2;
        no se estiman medias ni otros parámetros estadísticos.
        """
        self._ajustado = False
        self._validar_entrada(tabla)
        self._ajustado = True
        return self

    def transformar(self, tabla):
        """Valida también la nueva tabla y delega el trabajo sobre una copia."""
        if not self._ajustado:
            raise RuntimeError("Llamar a ajustar() antes de transformar().")
        self._validar_entrada(tabla)
        return self._aplicar(tabla.copy(deep=True))

    def _aplicar(self, tabla):
        """Cada clase hija implementa la operación que le corresponde."""
        raise NotImplementedError("La clase hija debe implementar _aplicar().")


class LimpiadorCodigos(Transformador):
    """Limpia códigos según F2 y conserva el resumen de la última limpieza."""

    def __init__(self, esquema):
        # Conservamos nuestras reglas aunque se edite el diccionario externo.
        self._esquema = deepcopy(esquema)
        columnas = [variable["nombre"] for variable in self._esquema["variables"]]
        super().__init__(columnas)
        self._resumen = None

    def ajustar(self, tabla):
        self._resumen = None
        return super().ajustar(tabla)

    def transformar(self, tabla):
        # Si la nueva ejecución falla, no mostramos un resumen anterior.
        self._resumen = None
        return super().transformar(tabla)

    def _aplicar(self, tabla):
        limpia, resumen = limpiar_codigos(tabla, self._esquema)
        self._resumen = resumen
        return limpia

    def resumen(self):
        """Devuelve una copia de la evidencia de una transformación completada."""
        if self._resumen is None:
            raise RuntimeError("Todavía no hay una limpieza completada.")
        return self._resumen.copy(deep=True)
