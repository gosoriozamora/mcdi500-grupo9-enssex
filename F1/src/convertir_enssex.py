"""Descarga y convierte la versión documentada de ENSSEX sin limpiar sus datos."""

import argparse
import csv
import hashlib
import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
import pyreadstat


SOURCE_PAGE = (
    "https://datos.gob.cl/dataset/encuesta-nacional-de-salud-sexualidad-y-genero-"
    "enssex-2022-2023/resource/80062904-7206-4d82-a0e8-611b428b0ef9"
)
SOURCE_URL = (
    "https://datos.gob.cl/dataset/c6983439-49f6-4e71-85fe-e8de6e73dae0/"
    "resource/80062904-7206-4d82-a0e8-611b428b0ef9/download/20241205_enssex_data.sav"
)
SOURCE_SHA256 = "0f4218b9553600dfd44e6b1f78d376b040a0e6f0d854453312c59a6497ec58ea"
EXPECTED_SHAPE = (20392, 1126)
CSV_NAME = "20241205_enssex_desde_sav.csv"
METADATA_NAME = "etiquetas_y_metadatos_ENSSEX.json"


def sha256_file(path):
    """Calcula la huella sin cargar el archivo completo en memoria."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_source(path):
    if not path.is_file():
        raise FileNotFoundError(f"Falta el SAV: {path}. Descárguelo o use --download.")
    actual = sha256_file(path)
    if actual != SOURCE_SHA256:
        raise ValueError(
            "La huella del SAV no coincide con la versión documentada. "
            f"Esperada: {SOURCE_SHA256}. Observada: {actual}. "
            "Revise la descarga o el cambio de versión antes de continuar."
        )
    return actual


def obtain_source(path, download=False):
    """Reutiliza el SAV existente o descarga y verifica uno nuevo."""
    if path.exists() or not download:
        verify_source(path)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="descarga_enssex_", dir=path.parent) as temporary:
        candidate = Path(temporary) / "descarga.sav"
        request = Request(SOURCE_URL, headers={"User-Agent": "ENSSEX-reproducibilidad/1.0"})
        with urlopen(request, timeout=60) as response, candidate.open("wb") as stream:
            shutil.copyfileobj(response, stream)
        verify_source(candidate)
        shutil.copyfile(candidate, path)
    return True


def validate_csv(frame, csv_path):
    """Contrasta filas, columnas, valores y estructura contra la lectura del SAV."""
    back = pd.read_csv(
        csv_path, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False
    )
    if back.shape != frame.shape or back.columns.tolist() != frame.columns.tolist():
        raise ValueError("El CSV no conserva las dimensiones o el orden de columnas.")
    numeric = set(frame.select_dtypes(include="number").columns)
    for column in frame.columns:
        if column in numeric:
            observed = pd.to_numeric(back[column].replace("", np.nan))
            np.testing.assert_allclose(
                observed.to_numpy(dtype=float),
                frame[column].to_numpy(dtype=float),
                rtol=1e-14, atol=0, equal_nan=True,
                err_msg=f"Cambió el contenido numérico de {column}",
            )
        else:
            expected = frame[column].map(lambda value: "" if pd.isna(value) else str(value))
            if back[column].tolist() != expected.tolist():
                raise ValueError(f"Cambió el contenido de texto o fecha de {column}.")
    records = 0
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        for records, row in enumerate(csv.reader(stream, delimiter=";"), start=1):
            if len(row) != frame.shape[1]:
                raise ValueError(f"Cantidad de campos incorrecta en el registro {records}.")
    if records != len(frame) + 1:
        raise ValueError("La cantidad de registros CSV no coincide con el SAV.")
    return {
        "rows": len(frame), "columns": len(frame.columns),
        "column_names_and_order": "OK", "numeric_values_and_missing": "OK",
        "text_and_dates": "OK", "csv_record_widths": "OK",
        "numeric_rtol": 1e-14, "numeric_atol": 0,
    }


def convert(source, output_dir, report_path, download=False):
    """Genera el CSV y sus metadatos; conserva originales y salidas diferentes."""
    csv_target = output_dir / CSV_NAME
    metadata_target = output_dir / METADATA_NAME
    paths = [source, csv_target, metadata_target, report_path]
    if len({path.resolve() for path in paths}) != len(paths):
        raise ValueError("El SAV, CSV, metadatos e informe deben tener rutas distintas.")
    downloaded = obtain_source(source, download)
    source_hash = verify_source(source)
    print("SAV verificado. Leyendo los datos...", flush=True)
    frame, meta = pyreadstat.read_sav(
        str(source), apply_value_formats=False, user_missing=True
    )
    if frame.shape != EXPECTED_SHAPE or not frame.columns.is_unique:
        raise ValueError("Las dimensiones o los nombres de columnas difieren de lo esperado.")
    metadata = {
        "source_file": source.name, "source_sha256": source_hash,
        "source_page": SOURCE_PAGE, "source_url": SOURCE_URL,
        "license": "Creative Commons CCZero (CC0)",
        "rows": len(frame), "columns": len(frame.columns),
        "column_names_to_labels": meta.column_names_to_labels,
        "variable_value_labels": meta.variable_value_labels,
        "variable_measure": meta.variable_measure,
        "original_variable_types": meta.original_variable_types,
        "missing_ranges": meta.missing_ranges,
        "source_encoding": meta.file_encoding,
        "reader": "pyreadstat " + pyreadstat.__version__,
        "pandas_version": pd.__version__,
        "read_options": {"apply_value_formats": False, "user_missing": True},
        "csv_options": {
            "sep": ";", "encoding": "utf-8-sig", "index": False,
            "decimal": ".", "na_rep": "", "lineterminator": "\\n",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="conversion_enssex_", dir=output_dir) as temporary:
        csv_candidate = Path(temporary) / CSV_NAME
        metadata_candidate = Path(temporary) / METADATA_NAME
        frame.to_csv(
            csv_candidate, sep=";", encoding="utf-8-sig", index=False,
            decimal=".", na_rep="", lineterminator="\n",
        )
        print("CSV generado. Comprobando valores y estructura...", flush=True)
        checks = validate_csv(frame, csv_candidate)
        metadata_candidate.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )
        candidates = [(csv_candidate, csv_target), (metadata_candidate, metadata_target)]
        for candidate, target in candidates:
            if target.exists() and sha256_file(candidate) != sha256_file(target):
                raise FileExistsError(
                    f"La salida existente es diferente: {target}. "
                    "Se conserva intacta; utilice otra carpeta de salida y revise la diferencia."
                )
        if sha256_file(source) != source_hash:
            raise ValueError("El SAV cambió durante la conversión.")
        for candidate, target in candidates:
            if not target.exists():
                shutil.copyfile(candidate, target)
    report = {
        "status": "OK",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_page": SOURCE_PAGE, "source_url": SOURCE_URL,
        "downloaded_this_run": downloaded,
        "source_file": source.name, "source_bytes": source.stat().st_size,
        "source_sha256": source_hash, "source_unchanged": True,
        "csv_file": csv_target.name, "csv_bytes": csv_target.stat().st_size,
        "csv_sha256": sha256_file(csv_target),
        "metadata_file": metadata_target.name,
        "metadata_sha256": sha256_file(metadata_target),
        "versions": {
            "python": platform.python_version(), "pyreadstat": pyreadstat.__version__,
            "pandas": pd.__version__, "numpy": np.__version__,
        },
        "checks": checks,
        "scope": "Conversión de formato; no incluye limpieza, selección ni recodificación.",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Conversión verificada: {len(frame)} filas y {len(frame.columns)} columnas.")
    print(f"Evidencia: {report_path}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("F1/data/raw/20241205_enssex_data.sav"))
    parser.add_argument("--output-dir", type=Path, default=Path("F1/data/raw"))
    parser.add_argument("--report", type=Path, default=Path("F1/docs/verificacion_conversion_enssex.json"))
    parser.add_argument("--download", action="store_true", help="Descargar el SAV oficial si aún no existe.")
    args = parser.parse_args()
    try:
        convert(args.source, args.output_dir, args.report, args.download)
    except (OSError, ValueError, AssertionError) as error:
        print(f"No se completó la conversión: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
