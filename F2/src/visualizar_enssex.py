"""Gráficos de diagnóstico de F2."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from presentacion_enssex import etiqueta_variable


def graficar_diagnostico(limpia, impacto, esquema):
    """Visualiza faltantes y tamaños de grupo, sin adelantar inferencias de F3."""
    fig, ejes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    faltan = impacto.loc[impacto['faltantes_despues'].gt(0)].sort_values('faltantes_despues')
    from textwrap import fill
    rotulos = [fill(etiqueta_variable(n, esquema), width=38) for n in faltan['variable']]
    ejes[0].barh(rotulos, 100*faltan['faltantes_despues']/len(limpia), color='#35749A')
    ejes[0].tick_params(axis='y', labelsize=9)
    ejes[0].set(xlabel='Porcentaje de las personas seleccionadas', title='Faltantes después de recodificar NS/NR')
    cantidades = limpia['p93'].value_counts(dropna=False).reindex([1, 2, 3, pd.NA], fill_value=0)
    ejes[1].bar(['Completa', 'Parcial', 'No depende', 'Sin respuesta'], cantidades.to_numpy(), color='#448578')
    ejes[1].set(ylabel='Personas', title='Dependencia económica de la pareja (p93)')
    ejes[1].tick_params(axis='x', rotation=20)
    for eje in ejes:
        eje.spines[['top', 'right']].set_visible(False)
    return fig



def graficar_edades(limpia):
    fig, ejes = plt.subplots(1, 2, figsize=(11, 3.8), constrained_layout=True)
    ejes[0].hist([limpia['p4'].dropna().astype(float), limpia['p91'].dropna().astype(float)],
                 bins=np.arange(15, 106, 5), label=['Persona encuestada (p4)', 'Pareja (p91)'], color=['#35749A', '#D19650'])
    ejes[0].set(xlabel='Edad en años', ylabel='Personas', title='Distribución de las edades')
    ejes[0].legend()
    ejes[1].hist((limpia['p4']-limpia['p91']).dropna().astype(float), bins=30, color='#448578')
    ejes[1].set(xlabel='Edad de la persona (p4) menos edad de la pareja (p91)', ylabel='Personas', title='Diferencia de edad con signo')
    for eje in ejes:
        eje.spines[['top', 'right']].set_visible(False)
    return fig
