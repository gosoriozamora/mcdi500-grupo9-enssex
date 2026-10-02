"""Casos de denominadores, ausencias superpuestas, orden y exportación de F4."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
for carpeta in ['F2/src', 'F3/src', 'F3/tests', 'F4/src']:
    sys.path.insert(0, str(RAIZ / carpeta))

from preparar_enssex import sha256_archivo
from pipeline_enssex import PipelineENSSEX
from exportacion_enssex import exportar_resultados_f3
from validar_pipeline import muestra_controlada, esperar_error
from datos_interpretables import exportar_interpretables, CSV
from analisis_descriptivo import construir_resumen, exportar_analisis, tablas_exportables
from visualizaciones import crear_figuras, guardar_figuras


def main():
    esquema = json.loads((RAIZ / 'F2/docs/esquema_variables_F2.json').read_text(encoding='utf-8'))
    variables = {v['nombre']: v for v in esquema['variables']}
    # Ocho personas: ausencias solapadas y bases distintas entre dimensiones.
    tabla = pd.DataFrame({'folio_encuesta': [str(i) for i in range(8)]})
    respuestas = {
        'p1': [None, 2, 1, 1, 2, 2, None, 1],  # Sexo asignado al nacer, con ausencias.
        'p93': [1, 1, 1, 2, 2, 3, None, None],  # Dependencia económica.
        'i_6_p9': [7, 1, None, 6, None, None, 5, None],  # Vida sexual.
        'i_2_p9': [6, None, 7, 5, 7, 1, None, 2],  # Bienestar mental o emocional.
    }
    for codigo, valores in respuestas.items():
        v = variables[codigo]
        tabla[codigo] = pd.Categorical(valores, categories=v['categorias'], ordered=v['ordenada'])
    original = tabla.copy(deep=True)
    resumen = construir_resumen(tabla, esquema)
    pd.testing.assert_frame_equal(tabla, original, check_exact=True)
    assert resumen['dependencia']['validos'] == 6
    assert resumen['dependencia']['ausentes'] == 2
    assert [f['personas'] for f in resumen['dependencia']['distribucion']] == [3, 2, 1]
    assert resumen['dependencia']['distribucion'][0]['porcentaje'] == 50
    sexual = resumen['comparaciones']['i_6_p9']  # Valoración de la vida sexual.
    emocional = resumen['comparaciones']['i_2_p9']  # Bienestar mental o emocional.
    assert (sexual['base_comparacion'], sexual['excluidos_comparacion']) == (3, 5)
    assert (emocional['base_comparacion'], emocional['excluidos_comparacion']) == (5, 3)
    assert sexual['ausentes_ambas_variables'] == emocional['ausentes_ambas_variables'] == 1
    assert resumen['base_comun']['personas'] == 2
    assert [f['validos'] for f in sexual['denominadores']] == [2, 1, 0]
    assert [f['ausentes'] for f in sexual['denominadores']] == [1, 1, 1]
    assert [f['validos'] for f in emocional['denominadores']] == [2, 2, 1]
    assert [f['codigo_respuesta'] for f in sexual['distribucion'][:7]] == list(range(1, 8))
    assert sexual['distribucion'][0]['porcentaje'] == 50
    assert sexual['distribucion'][1]['personas'] == 0
    assert sexual['distribucion'][1]['porcentaje'] == 0
    assert all(f['porcentaje'] is None for f in sexual['distribucion'][14:])
    hombres, mujeres = resumen['por_sexo']['grupos']
    sin_sexo = resumen['por_sexo']['sin_respuesta']
    assert [hombres['personas'], mujeres['personas'], sin_sexo['personas']] == [3, 3, 2]
    assert [hombres['dependencia']['validos'], mujeres['dependencia']['validos'], sin_sexo['dependencia']['validos']] == [2, 3, 1]
    # Los denominadores son internos al sexo y a la dependencia, no al total.
    assert [g['comparaciones']['i_6_p9']['base_comparacion'] for g in [hombres, mujeres, sin_sexo]] == [1, 1, 1]
    assert [g['comparaciones']['i_2_p9']['base_comparacion'] for g in [hombres, mujeres, sin_sexo]] == [2, 2, 1]
    assert hombres['comparaciones']['i_6_p9']['distribucion'][12]['porcentaje'] == 100
    assert mujeres['comparaciones']['i_6_p9']['distribucion'][0]['porcentaje'] == 100
    for codigo in ['i_6_p9', 'i_2_p9']:
        general = resumen['comparaciones'][codigo]['distribucion']
        for i, fila in enumerate(general):
            assert sum(g['comparaciones'][codigo]['distribucion'][i]['personas']
                       for g in [hombres, mujeres, sin_sexo]) == fila['personas']
    tablas = tablas_exportables(resumen)
    assert len(tablas) == 8
    assert len(tablas['denominadores_sexo']) == 18
    assert len(tablas['i_6_p9_sexo']) == 63
    assert sum(f['personas'] for f in tablas['i_6_p9_sexo']) == 3
    assert any(f['sexo'] == 'Sin respuesta' and f['personas'] == 1 for f in tablas['i_6_p9_sexo'])
    for caso in [tabla.iloc[:0], tabla.iloc[:1], tabla.iloc[-2:]]:
        salida = construir_resumen(caso, esquema)
        assert len(salida['dependencia']['distribucion']) == 3
        for comparacion in salida['comparaciones'].values():
            assert len(comparacion['distribucion']) == 21
            assert all(f['porcentaje'] is None for f in comparacion['distribucion'] if not f['denominador'])
    mala = tabla.copy(deep=True)
    mala.loc[1, 'folio_encuesta'] = mala.loc[0, 'folio_encuesta']
    esperar_error(ValueError, lambda: construir_resumen(mala, esquema))
    mala = tabla.copy(deep=True)
    mala['p93'] = mala['p93'].cat.add_categories([99])
    esperar_error(ValueError, lambda: construir_resumen(mala, esquema))
    mala = tabla.copy(deep=True)
    mala['i_6_p9'] = mala['i_6_p9'].cat.reorder_categories(list(range(7, 0, -1)))
    esperar_error(ValueError, lambda: construir_resumen(mala, esquema))
    mala = tabla.copy(deep=True)
    mala['p1'] = mala['p1'].cat.add_categories([99])
    esperar_error(ValueError, lambda: construir_resumen(mala, esquema))
    print('OK: denominadores específicos, ausencias superpuestas y base común calculados manualmente.')
    print('OK: categorías con cero, grupos sin base, tabla vacía y una persona; entradas intactas.')
    print('OK: rechazo de folios duplicados, categorías inesperadas y orden ordinal incorrecto.')
    print('OK: sexo asignado al nacer (p1), ausencias conservadas y conciliación exacta con el total.')
    with TemporaryDirectory() as temporal:
        temporal = Path(temporal)
        # Comprobar porcentajes realmente representados y escala común.
        figuras = crear_figuras(resumen)
        mapa_sexual = figuras['figura_2_valoracion_vida_sexual'].axes[0].images[0]
        mapa_emocional = figuras['figura_3_bienestar_mental_emocional'].axes[0].images[0]
        assert mapa_sexual.get_array()[0, 0] == 50
        assert mapa_sexual.get_array().mask[2].all()
        assert mapa_sexual.get_clim() == mapa_emocional.get_clim()
        for nombre, figura in figuras.items():
            if nombre == 'figura_1_dependencia_economica':
                continue
            assert len(figura.axes) == 4  # Total, hombre, mujer y escala de color.
            for eje in figura.axes[:3]:
                assert eje.images[0].get_clim() == mapa_sexual.get_clim()
        assert figuras['figura_2_valoracion_vida_sexual'].axes[1].images[0].get_array()[1, 5] == 100
        guardar_figuras(figuras, temporal / 'sin_base')
        resultados = PipelineENSSEX(esquema).ejecutar(muestra_controlada(esquema))
        exportar_resultados_f3(resultados, temporal / 'f3', esquema)
        exportar_interpretables(resultados['principal'], esquema, temporal / 'f3', temporal / 'f4')
        primera = exportar_analisis(temporal / 'f4', temporal / 'salida')
        segunda = exportar_analisis(temporal / 'f4', temporal / 'repeticion')
        assert primera['reproduccion']['productos'] == segunda['reproduccion']['productos']
        assert len(primera['reproduccion']['productos']) == 14
        ruta = temporal / 'salida' / 'resumen_analitico.json'
        assert json.loads(ruta.read_text(encoding='utf-8')) == primera
        tabla_csv = pd.read_csv(temporal / 'salida' / 'denominadores.csv', sep=';', encoding='utf-8-sig')
        assert len(tabla_csv) == 6
        assert tabla_csv['validos'].sum() == 2
        tabla_sexo = pd.read_csv(temporal / 'salida' / 'denominadores_por_sexo.csv', sep=';', encoding='utf-8-sig')
        assert len(tabla_sexo) == 18
        assert tabla_sexo['validos'].sum() == 2
        huella = sha256_archivo(ruta)
        esperar_error(FileExistsError, lambda: exportar_analisis(temporal / 'f4', temporal / 'salida'))
        assert sha256_archivo(ruta) == huella
        entrada = temporal / 'f4' / CSV
        entrada.write_bytes(entrada.read_bytes() + b'\n')
        esperar_error(ValueError, lambda: exportar_analisis(temporal / 'f4', temporal / 'alterado'))
        assert not (temporal / 'alterado').exists()
    print('OK: gráficos coherentes con tablas, escala común y tratamiento de grupos sin base.')
    print('OK: exportación reproducible, relectura de tablas y rechazo de sobrescritura o entrada alterada.')


if __name__ == '__main__':
    main()
