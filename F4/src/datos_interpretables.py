"""Copia interpretable de F3: conserva códigos y agrega etiquetas del esquema."""
import argparse
import json
from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'F2/src'))
sys.path.insert(0, str(RAIZ / 'F3/src'))

from exportacion_enssex import leer_resultados_f3, MANIFIESTO
from preparar_enssex import serializar_base, sha256_archivo

CSV = 'enssex_convivientes_F4_interpretable.csv'
REGISTRO = 'datos_interpretables_F4.json'


def preparar_interpretables(principal, esquema):
    """Devuelve una copia con columnas __etiqueta, sin imputar ni excluir filas.

    Recibe la tabla principal restaurada por leer_resultados_f3. Las categorías
    y su orden deben coincidir con el esquema; los faltantes siguen ausentes.
    """
    if not isinstance(principal, pd.DataFrame):
        raise TypeError('La entrada debe ser un DataFrame.')
    nombres = [v['nombre'] for v in esquema['variables']]
    if len(nombres) != len(set(nombres)) or not principal.columns.is_unique:
        raise ValueError('Nombres de columnas o variables duplicados.')
    if not set(nombres).issubset(principal.columns):
        raise ValueError('Faltan columnas del esquema en la tabla principal.')
    folios = principal['folio_encuesta']
    if folios.isna().any() or not folios.is_unique:
        raise ValueError('Los folios deben estar presentes y ser únicos.')
    if not principal[['p81', 'p83']].eq(1).all().all():
        raise ValueError('La tabla contiene personas fuera del filtro de convivencia.')
    salida = principal.copy(deep=True)
    for variable in esquema['variables']:
        categorias = variable['categorias']
        if not categorias:
            continue
        nombre = variable['nombre']
        serie = principal[nombre]
        if not isinstance(serie.dtype, pd.CategoricalDtype):
            raise ValueError(f'{nombre}: restaurar categorías mediante leer_resultados_f3.')
        if serie.cat.categories.tolist() != categorias or serie.cat.ordered != variable['ordenada']:
            raise ValueError(f'{nombre}: categorías u orden distintos del esquema.')
        etiquetas = [variable['etiquetas'].get(str(c)) for c in categorias]
        if any(not isinstance(e, str) or not e.strip() for e in etiquetas):
            raise ValueError(f'{nombre}: falta una etiqueta válida.')
        if len(set(etiquetas)) != len(etiquetas):
            raise ValueError(f'{nombre}: etiquetas duplicadas impiden recuperar los códigos.')
        destino = nombre + '__etiqueta'
        if destino in salida:
            raise ValueError(f'La columna {destino} ya existe.')
        salida[destino] = pd.Series(
            pd.Categorical.from_codes(serie.cat.codes, etiquetas, ordered=serie.cat.ordered),
            index=serie.index,
        )
    return salida


def leer_interpretables(carpeta):
    """Verifica la huella y restaura tipos, códigos, etiquetas y orden del CSV F4."""
    carpeta = Path(carpeta)
    registro = json.loads((carpeta / REGISTRO).read_text(encoding='utf-8'))
    if registro['version'] != 1:
        raise ValueError('Versión de datos interpretables no compatible.')
    ruta = carpeta / CSV
    if sha256_archivo(ruta) != registro['sha256_csv']:
        raise ValueError('La huella del CSV F4 no coincide.')
    tabla = pd.read_csv(ruta, sep=';', encoding='utf-8-sig', dtype='string',
                        keep_default_na=False, na_values=[''])
    if len(tabla) != registro['filas'] or tabla.columns.tolist() != registro['columnas']:
        raise ValueError('Filas o columnas distintas del registro F4.')
    for columna, tipo in registro['tipos'].items():
        if tipo == 'category':
            detalle = registro['categorias'][columna]
            valores = tabla[columna]
            if detalle['codigos']:
                valores = valores.astype('Int64')
            if not valores.dropna().isin(detalle['valores']).all():
                raise ValueError(f'{columna}: valor ajeno a las categorías declaradas.')
            tabla[columna] = pd.Categorical(valores, categories=detalle['valores'],
                                            ordered=detalle['ordenada'])
        elif tipo.startswith('datetime64['):
            tabla[columna] = pd.to_datetime(tabla[columna], format='%Y-%m-%d').astype(tipo)
        else:
            tabla[columna] = tabla[columna].astype(tipo)
    # No basta que las etiquetas existan: cada una debe corresponder a su código.
    principal = tabla[registro['columnas_principales']]
    esperada = preparar_interpretables(principal, registro['esquema'])
    pd.testing.assert_frame_equal(tabla, esperada, check_exact=True)
    return tabla


def exportar_interpretables(principal, esquema, entrada_f3, destino):
    """Exporta y comprueba relectura exacta en un destino sin productos anteriores."""
    destino = Path(destino)
    if any((destino / n).exists() for n in [CSV, REGISTRO]):
        raise FileExistsError('El destino ya contiene productos F4; elegir otro.')
    visual = preparar_interpretables(principal, esquema)
    registro = {
        'version': 1, 'filas': len(visual), 'columnas': visual.columns.tolist(),
        'columnas_principales': principal.columns.tolist(), 'esquema': esquema,
        'tipos': visual.dtypes.astype(str).to_dict(), 'categorias': {},
        'fuente_f3': {
            'carpeta': str(Path(entrada_f3)),
            'sha256_manifiesto': sha256_archivo(Path(entrada_f3) / MANIFIESTO),
        },
        'faltantes_centrales': {c: int(principal[c].isna().sum()) for c in esquema['centrales']},
        'politica': 'Conservar personas, códigos y ausencias; agregar etiquetas sin imputación.',
        'relectura_exacta': False,
    }
    for columna in visual:
        if isinstance(visual[columna].dtype, pd.CategoricalDtype):
            registro['categorias'][columna] = {
                'valores': visual[columna].cat.categories.tolist(),
                'ordenada': visual[columna].cat.ordered,
                'codigos': columna in principal.columns,
            }
    destino.mkdir(parents=True, exist_ok=True)
    serializar_base(visual, esquema).to_csv(
        destino / CSV, sep=';', encoding='utf-8-sig', index=False, na_rep='',
        date_format='%Y-%m-%d', lineterminator='\n',
    )
    registro['sha256_csv'] = sha256_archivo(destino / CSV)
    ruta_registro = destino / REGISTRO
    ruta_registro.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + '\n',
                             encoding='utf-8', newline='\n')
    pd.testing.assert_frame_equal(visual.reset_index(drop=True),
                                  leer_interpretables(destino), check_exact=True)
    registro['relectura_exacta'] = True
    ruta_registro.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + '\n',
                             encoding='utf-8', newline='\n')
    return registro


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', type=Path, default=RAIZ / 'F3/data/processed')
    parser.add_argument('--salida', type=Path, default=RAIZ / 'F4/data/processed')
    args = parser.parse_args()
    recuperadas = leer_resultados_f3(args.entrada)
    esquema = json.loads((args.entrada / MANIFIESTO).read_text(encoding='utf-8'))['esquema']
    registro = exportar_interpretables(recuperadas['principal'], esquema, args.entrada, args.salida)
    print(f"OK: {registro['filas']} personas; {len(registro['columnas'])} columnas con códigos y etiquetas.")
    print('OK: relectura exacta; conservación de faltantes, folios, valores y orden de categorías.')
    print('Ausencias centrales:', registro['faltantes_centrales'])


if __name__ == '__main__':
    main()
