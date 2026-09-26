"""Exportación y relectura de F3. Requiere F2/src en la ruta de importación."""
import json
from pathlib import Path

import pandas as pd

from preparar_enssex import (
    serializar_base, tipificar_categorias, codificar_nominales,
    validar_resultado, sha256_archivo,
)


ARCHIVOS = {
    'principal': 'enssex_convivientes_F3.csv',
    'nominales': 'enssex_convivientes_F3_nominales.csv',
}
MANIFIESTO = 'exportacion_F3.json'


def leer_resultados_f3(carpeta):
    """Comprueba las huellas y restaura tipos y categorías desde el manifiesto.

    El índice de filas se reconstruye desde cero; folio y orden se conservan.
    Las huellas detectan cambios en los CSV, no autentican el manifiesto.
    """
    carpeta = Path(carpeta)
    evidencia = json.loads((carpeta / MANIFIESTO).read_text(encoding='utf-8'))
    if evidencia['version'] != 1:
        raise ValueError('Versión de exportación no compatible.')
    esquema = evidencia['esquema']
    tablas = {}
    for nombre, archivo in ARCHIVOS.items():
        detalle = evidencia['productos'][nombre]
        ruta = carpeta / archivo
        if sha256_archivo(ruta) != detalle['sha256']:
            raise ValueError(f'La huella del CSV {nombre} no coincide.')
        # Primero texto: evita perder ceros iniciales y confundir "NA" con ausencia.
        tabla = pd.read_csv(ruta, sep=';', encoding='utf-8-sig', dtype='string',
                            keep_default_na=False, na_values=[''])
        if tabla.columns.tolist() != detalle['columnas'] or len(tabla) != detalle['filas']:
            raise ValueError(f'Dimensiones o columnas incorrectas en {nombre}.')
        for columna in tabla:
            tipo = detalle['tipos'][columna]
            if tipo == 'category':
                tabla[columna] = tabla[columna].astype('Int64')
            elif tipo.startswith('datetime64['):
                tabla[columna] = pd.to_datetime(tabla[columna], format='%Y-%m-%d').astype(tipo)
            elif nombre == 'nominales' and columna != 'folio_encuesta':
                valores = tabla[columna].astype('Int64')
                if valores.isna().any() or not valores.isin([0, 1]).all():
                    raise ValueError(f'Indicador nominal inválido: {columna}.')
                tabla[columna] = valores.astype(tipo)
            else:
                tabla[columna] = tabla[columna].astype(tipo)
        if nombre == 'principal':
            for variable in esquema['variables']:
                if variable['categorias']:
                    valores = tabla[variable['nombre']].dropna()
                    if not valores.isin(variable['categorias']).all():
                        raise ValueError(f"Categoría no documentada: {variable['nombre']}.")
            tabla = tipificar_categorias(tabla, esquema)
        tablas[nombre] = tabla
    principal = tablas['principal']
    if principal['folio_encuesta'].isna().any() or not principal['folio_encuesta'].is_unique:
        raise ValueError('Los folios deben estar presentes y ser únicos.')
    pd.testing.assert_frame_equal(
        tablas['nominales'], codificar_nominales(principal, esquema), check_exact=True
    )
    return tablas


def exportar_resultados_f3(resultados, carpeta, esquema):
    """Guarda dos CSV y un manifiesto, y comprueba la relectura exacta.

    Recibe la salida de PipelineENSSEX. Exige un destino sin estos tres archivos;
    no sobrescribe exportaciones anteriores. No modifica las tablas recibidas.
    """
    principal = resultados['principal']
    nominales = resultados['nominales']
    validaciones = validar_resultado(resultados['seleccion'], principal, nominales, esquema)
    pd.testing.assert_frame_equal(nominales, codificar_nominales(principal, esquema),
                                  check_exact=True)
    carpeta = Path(carpeta)
    rutas = [carpeta / archivo for archivo in [*ARCHIVOS.values(), MANIFIESTO]]
    if any(ruta.exists() for ruta in rutas):
        raise FileExistsError('El destino ya contiene productos F3; elija otra carpeta.')
    evidencia = {'version': 1, 'esquema': esquema, 'productos': {},
                 'indice': 'No exportado; relectura con RangeIndex. Folio y orden conservados.',
                 'comprobaciones_preexportacion': len(validaciones)}
    # Comprobar que el esquema se puede guardar antes de crear archivos.
    json.dumps(evidencia, ensure_ascii=False, allow_nan=False)
    carpeta.mkdir(parents=True, exist_ok=True)
    for nombre, archivo in ARCHIVOS.items():
        tabla = resultados[nombre]
        serial = serializar_base(tabla, esquema) if nombre == 'principal' else tabla
        ruta = carpeta / archivo
        serial.to_csv(ruta, sep=';', encoding='utf-8-sig', index=False, na_rep='',
                      date_format='%Y-%m-%d', lineterminator='\n')
        evidencia['productos'][nombre] = {
            'filas': len(tabla), 'columnas': tabla.columns.tolist(),
            'tipos': tabla.dtypes.astype(str).to_dict(), 'sha256': sha256_archivo(ruta),
        }
    (carpeta / MANIFIESTO).write_text(
        json.dumps(evidencia, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
        encoding='utf-8', newline='\n',
    )
    recuperadas = leer_resultados_f3(carpeta)
    for nombre in ARCHIVOS:
        pd.testing.assert_frame_equal(resultados[nombre].reset_index(drop=True),
                                      recuperadas[nombre], check_exact=True)
    return evidencia
