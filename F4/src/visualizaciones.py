"""Tres figuras descriptivas de F4 construidas a partir de sus tablas resumen."""
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

ESTILO = {
    'font.family': 'DejaVu Sans', 'font.size': 11,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.labelcolor': '#243746', 'text.color': '#243746',
    'xtick.color': '#243746', 'ytick.color': '#243746',
    'svg.hashsalt': 'enssex-f4', 'figure.facecolor': 'white',
}
FUENTE = 'Fuente: ENSSEX 2022–2023 · Elaboración propia · Muestra sin ponderación.'


def entero(numero):
    return f'{numero:,}'.replace(',', '.')


def decimal(numero):
    return f'{numero:.1f}'.replace('.', ',')


def figura_dependencia(resumen):
    """Barras desde cero con base válida y ausencias explícitas."""
    dep = resumen['dependencia']
    filas = dep['distribucion']
    with plt.rc_context(ESTILO):
        fig, ax = plt.subplots(figsize=(11.6, 5.7))
        fig.subplots_adjust(left=.26, right=.96, bottom=.27, top=.73)
        fig.text(.05, .94, '01  |  COMPOSICIÓN DE LA MUESTRA', fontsize=10, color='#52717d')
        fig.text(.05, .875, 'Dependencia económica entre quienes conviven con su pareja',
                 fontsize=17, weight='bold')
        fig.text(.05, .815, dep['variable'], fontsize=12)
        valores = [f['porcentaje'] if f['porcentaje'] is not None else 0 for f in filas]
        ax.barh(range(len(filas)), valores, height=.54, color='#267a8a')
        ax.set_yticks(range(len(filas)), [f['grupo'] for f in filas])
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}%'))
        ax.set_xlabel('Porcentaje de respuestas válidas')
        ax.set_axisbelow(True)
        ax.grid(axis='x', alpha=.2)
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y', length=0, pad=10)
        for i, (fila, valor) in enumerate(zip(filas, valores)):
            texto = (f"{decimal(valor)}%  ·  n = {entero(fila['personas'])}"
                     if fila['porcentaje'] is not None else 'Sin base para calcular porcentaje')
            ax.text(valor + 1.2 if valor < 75 else valor - 1.2, i, texto, va='center',
                    ha='left' if valor < 75 else 'right', fontsize=11,
                    color='#243746' if valor < 75 else 'white')
        fig.text(.05, .13, f"Base: {entero(dep['validos'])} respuestas válidas de {entero(resumen['personas'])} personas. "
                 f"Sin respuesta: {entero(dep['ausentes'])}.", fontsize=10)
        fig.text(.05, .07, FUENTE, fontsize=9, color='#52717d')
    return fig


def _panel_valoracion(ax, comparacion, variable, limite_color, mostrar_respuestas):
    """Dibuja una dimensión con denominadores de dependencia propios del panel."""
    grupos = comparacion['denominadores']
    categorias = variable['categorias']
    filas = comparacion['distribucion']
    valores = np.array([f['porcentaje'] if f['porcentaje'] is not None else np.nan
                        for f in filas]).reshape(len(grupos), len(categorias))
    mapa = plt.get_cmap('Blues').copy()
    mapa.set_bad('#ebedef')
    dibujo = ax.imshow(valores, vmin=0, vmax=limite_color, cmap=mapa, aspect='auto')
    ax.set_xticks(range(len(categorias)), [variable['etiquetas'][str(c)].replace(' ', '\n', 1)
                                          if c in (1, 7) else str(c) for c in categorias])
    ax.tick_params(axis='x', labelbottom=mostrar_respuestas)
    ax.set_yticks(range(len(grupos)), [f"{g['grupo']}\nn = {entero(g['validos'])} · ausentes: {entero(g['ausentes'])}"
                                     for g in grupos])
    ax.tick_params(axis='both', length=0, pad=8, labelsize=10)
    ax.set_xticks(np.arange(-.5, len(categorias), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(grupos), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=2)
    ax.tick_params(which='minor', bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(len(grupos)):
        for j in range(len(categorias)):
            valor = valores[i, j]
            texto = f'{decimal(valor)}%' if np.isfinite(valor) else 'Sin base'
            rgba = mapa(valor / limite_color) if np.isfinite(valor) else (1, 1, 1, 1)
            brillo = .2126 * rgba[0] + .7152 * rgba[1] + .0722 * rgba[2]
            ax.text(j, i, texto, ha='center', va='center', fontsize=11,
                    weight='bold', color='white' if brillo < .5 else '#243746')
    return dibujo


def figura_valoracion(resumen, codigo_variable, numero, limite_color):
    """Panel general y paneles de sexo asignado al nacer (p1), en escala común."""
    v = resumen['variables'][codigo_variable]
    general = resumen['comparaciones'][codigo_variable]
    paneles = [('Total', general)] + [(g['sexo'], g['comparaciones'][codigo_variable])
                                      for g in resumen['por_sexo']['grupos']]
    cantidad = len(paneles)
    with plt.rc_context(ESTILO):
        fig = plt.figure(figsize=(11.6, 10.2))
        fig.text(.05, .965, f'0{numero}  |  DISTRIBUCIÓN GENERAL Y DESAGREGADA',
                 fontsize=10, color='#52717d')
        fig.text(.05, .92, general['variable'], fontsize=17, weight='bold')
        fig.text(.05, .887, f"Filas: {resumen['dependencia']['variable']}", fontsize=11)
        fig.text(.05, .86, f"Paneles: {resumen['por_sexo']['variable']} · Escala de 1 (Muy mal) a 7 (Muy bien)",
                 fontsize=11)
        espacio = .62 / cantidad
        alto = espacio - .057
        for i, (nombre, comparacion) in enumerate(paneles):
            abajo = .20 + (cantidad - i - 1) * espacio
            ax = fig.add_axes([.25, abajo, .62, alto])
            dibujo = _panel_valoracion(ax, comparacion, v, limite_color, i == cantidad - 1)
            ax.set_title(f"{nombre} · Base: {entero(comparacion['base_comparacion'])} · "
                         f"Excluidas por ausencias: {entero(comparacion['excluidos_comparacion'])}",
                         loc='left', fontsize=11, weight='bold', pad=10)
        barra = fig.colorbar(dibujo, cax=fig.add_axes([.91, .20, .015, .62 - .057]))
        barra.set_label('Respuestas válidas del grupo (%)', fontsize=10)
        ax.set_xlabel('Respuesta declarada', labelpad=6)
        fig.text(.05, .10, 'Cada fila con base válida suma 100% antes de redondear. Escala de color común en todos los paneles y ambas figuras.',
                 fontsize=10)
        fig.text(.05, .075, 'n: respuestas válidas. Ausentes: valoración faltante dentro del grupo. Exclusiones: falta dependencia o valoración en el panel.', fontsize=9)
        ausentes_sexo = resumen['por_sexo']['sin_respuesta']['personas']
        fig.text(.05, .05, f"Sexo asignado al nacer (p1): {entero(ausentes_sexo)} sin respuesta; se conservan en Total. "
                 'Total reúne a las personas de los paneles desagregados.', fontsize=9)
        fig.text(.05, .025, FUENTE, fontsize=9, color='#52717d')
    return fig


def crear_figuras(resumen):
    """Mantiene la misma escala de color para total, sexos y ambas valoraciones."""
    conjuntos = [resumen, *resumen['por_sexo']['grupos']]
    maximo = max((f['porcentaje'] for conjunto in conjuntos for c in conjunto['comparaciones'].values()
                  for f in c['distribucion'] if f['porcentaje'] is not None), default=0)
    limite = max(10, math.ceil(maximo / 10) * 10)
    return {
        'figura_1_dependencia_economica': figura_dependencia(resumen),
        'figura_2_valoracion_vida_sexual': figura_valoracion(resumen, 'i_6_p9', 2, limite),
        'figura_3_bienestar_mental_emocional': figura_valoracion(resumen, 'i_2_p9', 3, limite),
    }


def guardar_figuras(figuras, destino):
    """Exporta PNG a 200 dpi y SVG vectorial sin sobrescribir figuras existentes."""
    destino = Path(destino)
    try:
        if any((destino / f'{nombre}.{ext}').exists() for nombre in figuras for ext in ('png', 'svg')):
            raise FileExistsError('Ya existen figuras con estos nombres en el destino.')
        destino.mkdir(parents=True, exist_ok=True)
        with plt.rc_context(ESTILO):
            for nombre, fig in figuras.items():
                fig.savefig(destino / f'{nombre}.png', dpi=200)
                fig.savefig(destino / f'{nombre}.svg', metadata={'Date': None})
    finally:
        for fig in figuras.values():
            plt.close(fig)
