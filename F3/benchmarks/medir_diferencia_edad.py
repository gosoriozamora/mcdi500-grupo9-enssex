"""Desde la raíz: python F3/benchmarks/medir_diferencia_edad.py --salida ruta.json.

Guarda evidencia JSON y un gráfico PNG con el mismo nombre, sin sobrescribirlos.
"""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'F2/src'))
sys.path.insert(0, str(RAIZ / 'F3/src'))

from preparar_enssex import (
    cargar_base, seleccionar_convivientes, limpiar_codigos, construir_derivadas,
    sha256_archivo, sha256_codigo,
)
from diferencia_edad import diferencia_con_bucle, diferencia_por_columnas
from medicion_algoritmos import medir_alternativas


def ejecutar(tamanos, repeticiones, ejecuciones, semilla):
    evidencia = json.loads((RAIZ / 'docs/datos/verificacion_conversion_enssex.json')
                           .read_text(encoding='utf-8'))
    ruta_esquema = RAIZ / 'F2/docs/esquema_variables_F2.json'
    esquema = json.loads(ruta_esquema.read_text(encoding='utf-8'))
    ruta_csv = RAIZ / 'data/raw' / evidencia['csv_file']
    base = cargar_base(ruta_csv, evidencia, esquema)
    seleccion, _ = seleccionar_convivientes(base, esquema)
    limpia, _ = limpiar_codigos(seleccion, esquema)
    respaldo = limpia.copy(deep=True)
    esperado = construir_derivadas(limpia)['diferencia_edad_pareja']
    if len(limpia) != 8579:
        raise AssertionError('La selección no tiene las 8.579 personas documentadas.')
    for funcion in (diferencia_con_bucle, diferencia_por_columnas):
        pd.testing.assert_series_equal(funcion(limpia), esperado, check_exact=True)
    print('Equivalencia con F2 comprobada; midiendo muestras de rendimiento...', flush=True)
    resultado = medir_alternativas(limpia, tamanos, repeticiones, ejecuciones, semilla)
    pd.testing.assert_frame_equal(limpia, respaldo, check_exact=True)
    if sha256_archivo(ruta_csv) != evidencia['csv_sha256']:
        raise AssertionError('El CSV original cambió durante la medición.')
    resultado.update({
        'fecha_utc': datetime.now(timezone.utc).isoformat(),
        'equivalencia_f2': 'OK', 'archivo_original_intacto': True,
        'archivo_fuente': ruta_csv.name, 'sha256_csv': evidencia['csv_sha256'],
        'esquema_sha256_normalizado_lf': sha256_codigo(ruta_esquema),
        'huellas_codigo_normalizadas_lf': {
            nombre: sha256_codigo(RAIZ / nombre) for nombre in (
                'F2/src/preparar_enssex.py', 'F3/src/diferencia_edad.py',
                'F3/src/medicion_algoritmos.py', 'F3/benchmarks/medir_diferencia_edad.py')
        },
        'entorno': {
            'python': platform.python_version(), 'sistema': platform.system(),
            'version_sistema': platform.release(), 'arquitectura': platform.machine(),
            'procesador': platform.processor(), 'pandas': version('pandas'),
            'numpy': version('numpy'), 'matplotlib': version('matplotlib'),
        },
        'condiciones': {
            'tiempo': 'timeit.Timer; cada bloque dividido por ejecuciones; menor repetición.',
            'incluye': 'Validación común, resta y construcción de la serie; descarte del resultado temporal.',
            'excluye': 'Carga, limpieza, muestreo, igualdad, hash, impresión y escritura de evidencia.',
            'orden': 'Tamaños crecientes; alternativas alternadas en cada repetición.',
            'gc': 'gc.collect antes de cada bloque; timeit desactiva GC durante el cronometraje.',
            'calentamiento': 'Ambas funciones ejecutadas para comprobar cada muestra antes de medir.',
            'memoria': 'Una ejecución separada; máximo de asignaciones rastreadas, no RSS total.',
            'serie': 'memory_usage(index=True, deep=True); incluye índice compartido, no temporales.',
            'limitacion': 'Entorno y procesos de fondo influyen; los tiempos no prueban por sí solos Big O.',
        },
    })
    return resultado


def guardar_grafico(resultado, destino):
    """Grafica las mediciones observadas sin ajustar ni extrapolar una curva."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ejes = plt.subplots(1, 2, figsize=(10, 4.4), constrained_layout=True)
    filas = [m['filas'] for m in resultado['mediciones']]
    for nombre, etiqueta, color in (
        ('bucle', 'Bucle', '#b45309'), ('columnas', 'Por columnas', '#0369a1'),
    ):
        valores = [m['resultados'][nombre] for m in resultado['mediciones']]
        ejes[0].plot(filas, [v['menor_segundos'] * 1000 for v in valores],
                     marker='o', label=etiqueta, color=color)
        ejes[1].plot(filas, [v['maximo_rastreado_bytes'] / 2**20 for v in valores],
                     marker='o', label=etiqueta, color=color)
    ejes[0].set(title='Menor tiempo por ejecución', ylabel='Milisegundos')
    ejes[1].set(title='Máximo de memoria rastreada', ylabel='MiB (no RSS total)')
    for eje in ejes:
        eje.set_xlabel('Filas de la muestra de rendimiento')
        eje.set_ylim(bottom=0)
        eje.grid(alpha=0.25)
        eje.legend()
        eje.ticklabel_format(axis='x', style='plain')
    fig.suptitle('Diferencia de edad: muestras con reemplazo, semilla 42'
                 if resultado['semilla'] == 42 else
                 f"Diferencia de edad: muestras con reemplazo, semilla {resultado['semilla']}")
    fig.savefig(destino, dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True)
    parser.add_argument('--tamanos', type=int, nargs='+', default=[1000, 5000, 20000, 50000])
    parser.add_argument('--repeticiones', type=int, default=5)
    parser.add_argument('--ejecuciones', type=int, default=5)
    parser.add_argument('--semilla', type=int, default=42)
    args = parser.parse_args()
    if args.salida.suffix.lower() != '.json':
        parser.error('La salida debe tener extensión .json.')
    grafico = args.salida.with_suffix('.png')
    if args.salida.exists() or grafico.exists():
        parser.error('Ya existe el JSON o PNG; elegir otro nombre para conservar la evidencia.')
    resultado = ejecutar(args.tamanos, args.repeticiones, args.ejecuciones, args.semilla)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    guardar_grafico(resultado, grafico)
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
                           encoding='utf-8', newline='\n')
    for medicion in resultado['mediciones']:
        for nombre, valores in medicion['resultados'].items():
            print(f"{medicion['filas']:>6} filas; {nombre}: "
                  f"menor {valores['menor_segundos'] * 1000:.4f} ms; "
                  f"máximo {valores['maximo_rastreado_bytes'] / 2**20:.4f} MiB; "
                  f"serie {valores['serie_devuelta_bytes'] / 2**20:.4f} MiB")
    print('OK: equivalencia por tamaño, fuente y entrada intactas. JSON y gráfico guardados.')
