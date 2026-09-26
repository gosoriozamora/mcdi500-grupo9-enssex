"""Desde la raíz: python F3/benchmarks/medir_lectura_sav.py --salida ruta.json."""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'F2/src'))
sys.path.insert(0, str(RAIZ / 'F3/src'))

from preparar_enssex import sha256_archivo, sha256_codigo
from medicion_lectura import medir_lecturas


def ejecutar(repeticiones=5, ejecuciones=1):
    evidencia = json.loads((RAIZ / 'docs/datos/verificacion_conversion_enssex.json').read_text(encoding='utf-8'))
    ruta_esquema = RAIZ / 'F2/docs/esquema_variables_F2.json'
    esquema = json.loads(ruta_esquema.read_text(encoding='utf-8'))
    ruta = RAIZ / 'data/raw' / evidencia['source_file']
    identidad = sha256_archivo(ruta)
    if identidad != evidencia['source_sha256']:
        raise ValueError('El SAV no coincide con el original verificado.')
    columnas = [v['nombre'] for v in esquema['variables']]
    print('SAV verificado. Comparando valores y metadatos antes de medir...', flush=True)
    medicion = medir_lecturas(ruta, columnas, repeticiones, ejecuciones)
    if sha256_archivo(ruta) != identidad:
        raise AssertionError('El SAV cambió durante la medición.')
    if medicion['filas'] != evidencia['checks']['rows'] or len(columnas) != 19:
        raise AssertionError('Dimensiones distintas de la base y selección documentadas.')
    medicion.update({
        'fecha_utc': datetime.now(timezone.utc).isoformat(),
        'archivo': ruta.name, 'archivo_bytes': ruta.stat().st_size, 'sha256_sav': identidad,
        'columnas_sav': evidencia['checks']['columns'],
        'esquema_sha256_normalizado_lf': sha256_codigo(ruta_esquema),
        'huellas_codigo_normalizadas_lf': {
            nombre: sha256_codigo(RAIZ / nombre) for nombre in
            ['F3/src/medicion_lectura.py', 'F3/benchmarks/medir_lectura_sav.py']
        },
        'entorno': {'python': platform.python_version(), 'sistema': platform.system(),
                    'version_sistema': platform.release(), 'arquitectura': platform.machine(),
                    'procesador': platform.processor(),
                    'pandas': version('pandas'), 'numpy': version('numpy'),
                    'pyreadstat': version('pyreadstat')},
        'condiciones': {
            'fuente': 'Mismo SAV local; sin descarga ni conversión a CSV.',
            'cache': 'Calentada por validación previa; no se vacía la caché del sistema.',
            'tiempo': 'timeit.Timer; segundos totales divididos por ejecuciones; menor repetición.',
            'gc': 'gc.collect antes de cada bloque; timeit desactiva GC durante el cronometraje.',
            'memoria': 'Una ejecución separada por alternativa; máximo rastreado por tracemalloc, no RSS total.',
            'resultado': 'memory_usage(deep=True) de la tabla devuelta; no incluye metadatos ni temporales.',
            'limitacion': 'Procesos de fondo y cachés pueden afectar resultados; cifras específicas de este entorno.',
        },
    })
    return medicion


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True)
    parser.add_argument('--repeticiones', type=int, default=5)
    parser.add_argument('--ejecuciones', type=int, default=1)
    args = parser.parse_args()
    if args.salida.exists():
        parser.error('La salida existe; elegir otro archivo para conservar la medición anterior.')
    resultado = ejecutar(args.repeticiones, args.ejecuciones)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
                           encoding='utf-8', newline='\n')
    for nombre, valores in resultado['resultados'].items():
        print(f"{nombre}: menor {valores['menor_segundos']:.6f} s; "
              f"máximo rastreado {valores['maximo_rastreado_bytes'] / 2**20:.2f} MiB; "
              f"tabla devuelta {valores['tabla_devuelta_bytes'] / 2**20:.2f} MiB")
    print('OK: equivalencia exacta, metadatos conservados y SAV intacto. Evidencia guardada.')
