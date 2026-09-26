"""Desde la raíz: python F3/tests/validar_exportacion.py. Usa destinos temporales."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'F2/src'))
sys.path.insert(0, str(RAIZ / 'F3/src'))

from preparar_enssex import cargar_base, sha256_archivo
from pipeline_enssex import PipelineENSSEX
from exportacion_enssex import exportar_resultados_f3, leer_resultados_f3, ARCHIVOS, MANIFIESTO
from validar_pipeline import muestra_controlada, esperar_error


def comprobar_ida_vuelta(resultados, esquema, carpeta):
    copias = {nombre: tabla.copy(deep=True) for nombre, tabla in resultados.items()}
    evidencia = exportar_resultados_f3(resultados, carpeta, esquema)
    leidas = leer_resultados_f3(carpeta)
    for nombre in ARCHIVOS:
        pd.testing.assert_frame_equal(resultados[nombre].reset_index(drop=True),
                                      leidas[nombre], check_exact=True)
    for nombre in resultados:
        pd.testing.assert_frame_equal(resultados[nombre], copias[nombre], check_exact=True)
    assert evidencia['comprobaciones_preexportacion'] == 130
    assert sorted(p.name for p in carpeta.iterdir()) == sorted([*ARCHIVOS.values(), MANIFIESTO])
    return evidencia


def comprobar_controlados(esquema, temporal):
    base = muestra_controlada(esquema)
    resultados = PipelineENSSEX(esquema).ejecutar(base)
    # Caso de serialización: preservar el folio textual recibido por el exportador.
    # F2 normaliza antes los folios numéricos; aquí probamos el límite de exportación.
    for nombre in ARCHIVOS:
        resultados[nombre]['folio_encuesta'] = resultados[nombre]['folio_encuesta'].str.zfill(4)
    carpeta = temporal / 'controlados'
    comprobar_ida_vuelta(resultados, esquema, carpeta)
    recuperada = leer_resultados_f3(carpeta)['principal']
    assert recuperada['folio_encuesta'].tolist() == ['0001', '0002']
    assert recuperada['diferencia_edad_pareja'].iloc[0] == -5
    assert pd.isna(recuperada['diferencia_edad_pareja'].iloc[1])
    assert recuperada['p93'].cat.ordered
    assert not recuperada['p3'].cat.ordered
    assert recuperada.index.tolist() == [0, 1]
    for nombre, muestra in [('una_persona', base.iloc[:1]), ('centrales_ausentes', base.iloc[1:2])]:
        comprobar_ida_vuelta(PipelineENSSEX(esquema).ejecutar(muestra), esquema, temporal / nombre)
    print('OK: relectura exacta de valores, tipos, categorías, orden, fechas y faltantes.')
    print('OK: folios con ceros iniciales, una persona y categorías sin observaciones.')

    huellas = {p.name: sha256_archivo(p) for p in carpeta.iterdir()}
    esperar_error(FileExistsError, lambda: exportar_resultados_f3(resultados, carpeta, esquema))
    assert huellas == {p.name: sha256_archivo(p) for p in carpeta.iterdir()}
    erroneos = dict(resultados)
    erroneos['nominales'] = resultados['nominales'].copy(deep=True)
    erroneos['nominales'].iloc[0, 1] = 2
    destino = temporal / 'entrada_invalida'
    esperar_error(AssertionError, lambda: exportar_resultados_f3(erroneos, destino, esquema))
    assert not destino.exists()
    ruta = carpeta / ARCHIVOS['principal']
    respaldo = ruta.read_bytes()
    ruta.write_bytes(respaldo + b'\n')
    esperar_error(ValueError, lambda: leer_resultados_f3(carpeta))
    ruta.write_bytes(respaldo)
    print('OK: rechaza sobrescritura, productos inválidos y cambios en los bytes del CSV.')

    # Incluso si se recalcula la huella, una categoría desconocida no pasa a NA en silencio.
    texto = pd.read_csv(ruta, sep=';', encoding='utf-8-sig', dtype='string', keep_default_na=False)
    texto.loc[0, 'p93'] = '7'
    texto.to_csv(ruta, sep=';', encoding='utf-8-sig', index=False, lineterminator='\n')
    manifiesto = carpeta / MANIFIESTO
    contenido = manifiesto.read_bytes()
    evidencia = json.loads(contenido)
    evidencia['productos']['principal']['sha256'] = sha256_archivo(ruta)
    manifiesto.write_text(json.dumps(evidencia), encoding='utf-8')
    esperar_error(ValueError, lambda: leer_resultados_f3(carpeta))
    ruta.write_bytes(respaldo)
    manifiesto.write_bytes(contenido)
    ruta_nom = carpeta / ARCHIVOS['nominales']
    respaldo_nom = ruta_nom.read_bytes()
    nominal = pd.read_csv(ruta_nom, sep=';', encoding='utf-8-sig', dtype='string')
    nominal.iloc[0, 1] = '256'
    nominal.to_csv(ruta_nom, sep=';', encoding='utf-8-sig', index=False, lineterminator='\n')
    evidencia = json.loads(contenido)
    evidencia['productos']['nominales']['sha256'] = sha256_archivo(ruta_nom)
    manifiesto.write_text(json.dumps(evidencia), encoding='utf-8')
    esperar_error(ValueError, lambda: leer_resultados_f3(carpeta))
    ruta_nom.write_bytes(respaldo_nom)
    manifiesto.write_bytes(contenido)
    leer_resultados_f3(carpeta)
    print('OK: rechaza categorías desconocidas e indicadores fuera de 0/1 antes de convertirlos.')


def comprobar_reales(esquema, temporal):
    evidencia = json.loads((RAIZ / 'docs/datos/verificacion_conversion_enssex.json').read_text(encoding='utf-8'))
    ruta_base = RAIZ / 'data/raw' / evidencia['csv_file']
    protegidas = [ruta_base, *sorted((RAIZ / 'F2/data/processed').glob('*.csv'))]
    huellas = {p: sha256_archivo(p) for p in protegidas}
    base = cargar_base(ruta_base, evidencia, esquema)
    resultados = PipelineENSSEX(esquema).ejecutar(base)
    primera = comprobar_ida_vuelta(resultados, esquema, temporal / 'real_1')
    segunda = comprobar_ida_vuelta(resultados, esquema, temporal / 'real_2')
    assert primera == segunda
    for archivo in [*ARCHIVOS.values(), MANIFIESTO]:
        assert (temporal / 'real_1' / archivo).read_bytes() == (temporal / 'real_2' / archivo).read_bytes()
    assert resultados['principal'].shape == (8579, 20)
    assert resultados['nominales'].shape == (8579, 65)
    assert huellas == {p: sha256_archivo(p) for p in protegidas}
    print('OK: ENSSEX real recuperado exactamente: 8.579 personas, 20 columnas y matriz de 65.')
    print('OK: dos exportaciones idénticas byte a byte en este entorno; 130 comprobaciones previas.')
    print('OK: tablas recibidas, base original y CSV de F2 intactos. Solo destinos temporales.')


if __name__ == '__main__':
    esquema = json.loads((RAIZ / 'F2/docs/esquema_variables_F2.json').read_text(encoding='utf-8'))
    with TemporaryDirectory() as carpeta:
        comprobar_controlados(esquema, Path(carpeta))
        comprobar_reales(esquema, Path(carpeta))
