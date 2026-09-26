"""Estrategias descriptivas sobre copias; las imputaciones no son respuestas.

Requiere F2/src y F3/src en la ruta de importación. La entrada es la tabla
limpia, antes de tipificar categorías. Cada objeto se vincula con una selección
original: no es un estimador para entrenamiento y predicción sobre otra muestra.
"""
from copy import deepcopy

import pandas as pd

from preparar_enssex import normalizar_variable, validar_columnas
from transformadores import Transformador


def conservar_faltantes(serie, elegibles, grupos):
    """Conserva valores, ausencias, índice y tipo."""
    return serie.copy(deep=True)


def casos_disponibles(serie, elegibles, grupos):
    """Selecciona respuestas disponibles solo para este cálculo."""
    return serie.dropna().copy(deep=True)


def media_global(serie, elegibles, grupos):
    """Simula la media de códigos observados solo en no respuestas elegibles."""
    salida = serie.astype('Float64')
    salida.loc[elegibles] = salida.mean()
    return salida


def mediana_global(serie, elegibles, grupos):
    """Simula la mediana; no redondea ni convierte la simulación en categoría."""
    salida = serie.astype('Float64')
    salida.loc[elegibles] = salida.median()
    return salida


def mediana_por_dependencia(serie, elegibles, grupos):
    """Sin grupo o sin observaciones en el grupo, la ausencia permanece."""
    salida = serie.astype('Float64')
    medianas = salida.groupby(grupos, dropna=True).transform('median')
    salida.loc[elegibles] = medianas.loc[elegibles]
    return salida


ESTRATEGIAS = {
    conservar_faltantes: 'Conservar faltantes',
    casos_disponibles: 'Eliminar solo para este cálculo',
    media_global: 'Imputar media global',
    mediana_global: 'Imputar mediana global',
    mediana_por_dependencia: 'Imputar mediana por dependencia',
}


class TratamientoFaltantes(Transformador):
    """Aplica una estrategia a una central y conserva evidencia del escenario.

La selección original y el esquema se copian al construir el objeto. ajustar()
valida la correspondencia; transformar() la vuelve a comprobar. Las estadísticas
se calculan sobre la misma muestra descriptiva, no se aprenden para otra tabla.
Solo se simulan reemplazos en códigos de no respuesta explícitos del esquema.
"""

    def __init__(self, esquema, variable, estrategia, seleccion_original):
        if variable not in ('p93', 'i_6_p9', 'i_2_p9'):
            raise ValueError('Este componente solo admite las tres centrales.')
        if estrategia not in ESTRATEGIAS:
            raise ValueError('Estrategia no admitida en esta comparación.')
        if estrategia is mediana_por_dependencia and variable == 'p93':
            raise ValueError('No se imputa dependencia agrupando por sí misma.')
        if not isinstance(seleccion_original, pd.DataFrame):
            raise TypeError('La selección original debe ser un DataFrame.')
        columnas = [variable]
        if estrategia is mediana_por_dependencia:
            columnas.append('p93')
        validar_columnas(seleccion_original, columnas)
        if not seleccion_original.index.is_unique:
            raise ValueError('El índice original debe ser único.')
        self._esquema = deepcopy(esquema)
        self._reglas = {v['nombre']: v for v in self._esquema['variables']}
        for nombre in columnas:
            if nombre not in self._reglas or self._reglas[nombre]['tipo'] != 'ordinal':
                raise ValueError('Falta una regla ordinal para la comparación.')
        self._original = seleccion_original[columnas].copy(deep=True)
        self._variable = variable
        self._estrategia = estrategia
        self._resumen = None
        super().__init__(columnas)

    def _validar_entrada(self, tabla):
        super()._validar_entrada(tabla)
        if not tabla.index.equals(self._original.index):
            raise ValueError('La tabla y la selección original deben corresponder.')
        for nombre in self._columnas:
            esperada = normalizar_variable(self._original[nombre], self._reglas[nombre])
            if not tabla[nombre].equals(esperada):
                raise ValueError(f'{nombre} debe coincidir con su limpieza de F2.')

    def ajustar(self, tabla):
        self._resumen = None
        return super().ajustar(tabla)

    def transformar(self, tabla):
        self._resumen = None
        return super().transformar(tabla)

    def _aplicar(self, tabla):
        nombre = self._variable
        serie = tabla[nombre]
        regla = self._reglas[nombre]
        elegibles = self._original[nombre].isin(regla['no_respuesta']) & serie.isna()
        grupos = tabla['p93'] if self._estrategia is mediana_por_dependencia else None
        candidata = self._estrategia(serie.copy(deep=True), elegibles, grupos)
        salida = tabla.loc[candidata.index].copy(deep=True)
        salida[nombre] = candidata
        valores = candidata.dropna().astype(float)
        observados = serie.dropna().astype(float)
        var_original = observados.var(ddof=0)
        var_final = valores.var(ddof=0)
        reemplazados = serie.loc[candidata.index].isna() & candidata.notna()
        self._resumen = pd.DataFrame([{
            'variable': nombre,
            'alternativa': ESTRATEGIAS[self._estrategia],
            'filas_entrada': len(tabla),
            'filas': len(salida),
            'filas_excluidas': len(tabla) - len(salida),
            'elegibles': int(elegibles.sum()),
            'vacios_originales_protegidos': int(self._original[nombre].isna().sum()),
            'faltantes': int(candidata.isna().sum()),
            'imputados': int(reemplazados.sum()),
            'valores_fraccionarios': int((valores != valores.round()).sum()),
            'fuera_de_categorias': int((~valores.isin(regla['categorias'])).sum()),
            'varianza_codigos': var_final,
            'cambio_varianza_pct': 100 * (var_final / var_original - 1)
                if var_original > 0 else float('nan'),
        }])
        return salida

    def resumen(self):
        """Devuelve evidencia independiente; exige una transformación exitosa."""
        if self._resumen is None:
            raise RuntimeError('Todavía no hay un tratamiento completado.')
        return self._resumen.copy(deep=True)
