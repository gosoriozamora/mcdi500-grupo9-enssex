"""Casos controlados de etiquetas, ausencias, corrupción y relectura de F4."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
for carpeta in ['F2/src', 'F3/src', 'F3/tests', 'F4/src']:
    sys.path.insert(0, str(RAIZ / carpeta))

from pipeline_enssex import PipelineENSSEX
from exportacion_enssex import exportar_resultados_f3, leer_resultados_f3
from validar_pipeline import muestra_controlada, esperar_error
from datos_interpretables import preparar_interpretables, exportar_interpretables, leer_interpretables, CSV, REGISTRO
from preparar_enssex import sha256_archivo


def main():
    esquema = json.loads((RAIZ / 'F2/docs/esquema_variables_F2.json').read_text(encoding='utf-8'))
    principal = PipelineENSSEX(esquema).ejecutar(muestra_controlada(esquema))['principal']
    respaldo = principal.copy(deep=True)
    visual = preparar_interpretables(principal, esquema)
    pd.testing.assert_frame_equal(principal, respaldo, check_exact=True)
    pd.testing.assert_frame_equal(visual[principal.columns], principal, check_exact=True)
    assert visual.loc[10, 'p93__etiqueta'] == 'Sí, completamente'
    assert visual.loc[10, 'i_6_p9__etiqueta'] == '7 Muy bien'
    assert visual['i_6_p9__etiqueta'].cat.categories.tolist() == ['1 Muy mal', '2', '3', '4', '5', '6', '7 Muy bien']
    assert visual['i_6_p9__etiqueta'].cat.ordered
    assert visual['p93__etiqueta'].isna().equals(principal['p93'].isna())
    for tabla in [principal.iloc[:1], principal.iloc[1:2], principal.iloc[:0]]:
        salida = preparar_interpretables(tabla, esquema)
        pd.testing.assert_frame_equal(salida[tabla.columns], tabla, check_exact=True)
    esperar_error(ValueError, lambda: preparar_interpretables(visual, esquema))
    mala = principal.copy(deep=True)
    mala['folio_encuesta'] = ['1', '1']
    esperar_error(ValueError, lambda: preparar_interpretables(mala, esquema))
    mala = principal.copy(deep=True)
    mala['p93'] = mala['p93'].cat.add_categories([9])
    mala.loc[10, 'p93'] = 9
    esperar_error(ValueError, lambda: preparar_interpretables(mala, esquema))
    reglas = deepcopy(esquema)
    reglas['variables'][0]['etiquetas']['2'] = reglas['variables'][0]['etiquetas']['1']
    esperar_error(ValueError, lambda: preparar_interpretables(principal, reglas))
    reglas = deepcopy(esquema)
    del reglas['variables'][0]['etiquetas']['1']
    esperar_error(ValueError, lambda: preparar_interpretables(principal, reglas))
    with TemporaryDirectory() as temporal:
        temporal = Path(temporal)
        resultados = PipelineENSSEX(esquema).ejecutar(muestra_controlada(esquema))
        exportar_resultados_f3(resultados, temporal / 'f3', esquema)
        entrada = leer_resultados_f3(temporal / 'f3')['principal']
        destino = temporal / 'f4'
        exportar_interpretables(entrada, esquema, temporal / 'f3', destino)
        pd.testing.assert_frame_equal(preparar_interpretables(entrada, esquema), leer_interpretables(destino), check_exact=True)
        esperar_error(FileExistsError, lambda: exportar_interpretables(entrada, esquema, temporal / 'f3', destino))
        ruta = destino / CSV
        contenido = ruta.read_bytes()
        ruta.write_bytes(contenido + b'\n')
        esperar_error(ValueError, lambda: leer_interpretables(destino))
        ruta.write_bytes(contenido)
        texto = pd.read_csv(ruta, sep=';', encoding='utf-8-sig', dtype='string', keep_default_na=False)
        texto.loc[0, 'p93__etiqueta'] = 'No'
        texto.to_csv(ruta, sep=';', encoding='utf-8-sig', index=False, lineterminator='\n')
        registro = json.loads((destino / REGISTRO).read_text(encoding='utf-8'))
        registro['sha256_csv'] = sha256_archivo(ruta)
        (destino / REGISTRO).write_text(json.dumps(registro), encoding='utf-8')
        esperar_error(AssertionError, lambda: leer_interpretables(destino))
    print('OK: códigos intactos, etiquetas exactas, categorías no observadas y orden ordinal.')
    print('OK: una persona, todas las centrales ausentes y tabla vacía, sin modificar entradas.')
    print('OK: rechaza folios duplicados, códigos inesperados y etiquetas ambiguas o incompletas.')
    print('OK: relectura exacta, rechazo de sobrescritura y detección de CSV o etiquetas alteradas.')


if __name__ == '__main__':
    main()
