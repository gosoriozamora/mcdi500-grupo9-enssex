"""Coordina el preprocesamiento de ENSSEX en memoria, sin escribir archivos.

Requiere F2/src y F3/src en la ruta de importación. La base debe cargarse con
la verificación de identidad de F2 antes de llamar a ejecutar().
"""
from copy import deepcopy

import pandas as pd

from preparar_enssex import (
    seleccionar_convivientes, construir_derivadas, codificar_nominales,
    validar_resultado, disponibilidad_analisis,
)
from transformadores import LimpiadorCodigos, TipificadorCategorias
from faltantes import TratamientoFaltantes, conservar_faltantes


class PipelineENSSEX:
    """Compone funciones y transformadores bajo la política de conservación.

El esquema se copia al construir el objeto. Cada ejecución crea transformadores
propios y devuelve tablas independientes; no conserva resultados de otra corrida.
Las simulaciones de imputación se ejecutan fuera de este flujo principal.
"""

    def __init__(self, esquema):
        self._esquema = deepcopy(esquema)

    def ejecutar(self, base):
        """Recibe la base original cargada y devuelve productos y evidencia.

Rechaza entradas incorrectas antes de devolver resultados. No descarga, exporta
ni altera archivos. Las dimensiones esperadas del conjunto real se comprueban
en las pruebas; también admite muestras pequeñas para verificar casos límite.
"""
        if not isinstance(base, pd.DataFrame):
            raise TypeError('La base debe ser un DataFrame de pandas.')
        if not base.index.is_unique:
            raise ValueError('La base debe tener un índice único.')
        seleccion, flujo = seleccionar_convivientes(base, self._esquema)
        limpiador = LimpiadorCodigos(self._esquema)
        tratamientos = [
            TratamientoFaltantes(self._esquema, nombre, conservar_faltantes, seleccion)
            for nombre in self._esquema['centrales']
        ]
        tipificador = TipificadorCategorias(self._esquema)

        # Composición: el pipeline utiliza objetos con tareas específicas.
        etapas = [limpiador] + tratamientos + [tipificador]
        tabla = seleccion
        limpia = None
        for etapa in etapas:
            # Polimorfismo: la misma llamada ejecuta la operación de cada hija.
            tabla = etapa.ajustar(tabla).transformar(tabla)
            if etapa is limpiador:
                limpia = tabla.copy(deep=True)

        tipificada = tabla
        principal = construir_derivadas(tipificada)
        nominales = codificar_nominales(principal, self._esquema)
        validaciones = validar_resultado(seleccion, principal, nominales, self._esquema)
        resultados = {
            'seleccion': seleccion,
            'limpia': limpia,
            'tipificada': tipificada,
            'principal': principal,
            'nominales': nominales,
            'flujo_seleccion': flujo,
            'resumen_limpieza': limpiador.resumen(),
            'resumen_faltantes': pd.concat(
                [objeto.resumen() for objeto in tratamientos], ignore_index=True
            ),
            'disponibilidad': disponibilidad_analisis(limpia, self._esquema),
            'validaciones': validaciones,
        }
        return {nombre: tabla.copy(deep=True) for nombre, tabla in resultados.items()}
