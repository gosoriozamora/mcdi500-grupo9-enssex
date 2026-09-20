# Obtención y conversión de los datos ENSSEX

El proyecto utiliza la base ENSSEX 2022–2023 del Ministerio de Salud de Chile. Se conserva el archivo original en formato SPSS y se genera una copia CSV para trabajar en Python. La conversión mantiene todas las filas y columnas; la selección de convivientes, el tratamiento de no respuesta y las transformaciones analíticas corresponden a la preparación posterior de los datos.

## Fuente, licencia y versión

La [ficha oficial del recurso SAV](https://datos.gob.cl/dataset/encuesta-nacional-de-salud-sexualidad-y-genero-enssex-2022-2023/resource/80062904-7206-4d82-a0e8-611b428b0ef9) identifica al Ministerio de Salud como institución responsable y declara la licencia **Creative Commons CCZero (CC0)**. La ficha informa una actualización de los datos del 21 de julio de 2025. El archivo se denomina `20241205_enssex_data.sav`; su nombre no reemplaza la fecha de actualización indicada por el portal.

- [Descarga directa del SAV](https://datos.gob.cl/dataset/c6983439-49f6-4e71-85fe-e8de6e73dae0/resource/80062904-7206-4d82-a0e8-611b428b0ef9/download/20241205_enssex_data.sav).
- [Manual de uso y libro de códigos](https://datos.gob.cl/dataset/encuesta-nacional-de-salud-sexualidad-y-genero-enssex-2022-2023/resource/e155a68f-13f4-48e0-81e0-123f5c23433f).

La descarga realizada el 20/09/2026 coincide con el SAV conservado inicialmente por el equipo. La versión utilizada tiene **41.227.608 bytes, 20.392 registros y 1.126 columnas**. Su huella SHA-256 es:

```text
0f4218b9553600dfd44e6b1f78d376b040a0e6f0d854453312c59a6497ec58ea
```

El manual describe 923 variables; aquí se registran las dimensiones comprobadas en esta copia, sin atribuir una causa no verificada a la diferencia. La huella identifica el contenido del archivo y permite detectar una descarga incompleta o una versión distinta.

## Archivos y ubicaciones

Las rutas de esta tabla parten de la raíz del repositorio:

| Archivo | Función | Control de versiones |
|---|---|---|
| `F1/src/convertir_enssex.py` | Descarga opcional, conversión y comprobaciones. | Se incorpora a Git. |
| `F1/data/raw/20241205_enssex_data.sav` | Original descargado, que se conserva sin modificar. | Excluido de Git. |
| `F1/data/raw/20241205_enssex_desde_sav.csv` | Copia CSV completa para lectura desde los notebooks. | Excluido de Git. |
| `F1/data/raw/etiquetas_y_metadatos_ENSSEX.json` | Etiquetas, categorías y características de la base que el CSV no conserva por sí solo. | Excluido de Git; se regenera con el script. |
| `F1/docs/verificacion_conversion_enssex.json` | Huellas, versiones, dimensiones y resultados de las comprobaciones. | Evidencia que se incorpora a Git. |

La copia CSV convertida conserva el contenido original y por eso se ubica junto al SAV en `data/raw`. Los datos que posteriormente se limpien o transformen se guardarán en `data/processed`.

## Preparar el entorno

Seguir la [guía de instalación y ejecución](Instalacion_y_ejecucion.md). Desde la raíz del repositorio, en Git Bash:

```bash
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python -m pip check
```

La conversión comprobada utiliza Python 3.13.15, pandas 3.0.5, NumPy 2.5.3 y **pyreadstat 1.3.6**. Esta última biblioteca se añadió a `requirements.txt` para que el procedimiento funcione también en una instalación nueva. Quienes hayan preparado el entorno antes de esa incorporación deben volver a instalar desde el archivo de dependencias.

## Descargar y convertir

Desde la raíz del repositorio:

```bash
python F1/src/convertir_enssex.py --download
```

Si el SAV no está disponible, el script lo descarga desde el enlace oficial y comprueba su huella antes de conservarlo en `F1/data/raw`. Si ya existe, verifica y reutiliza ese archivo. Una huella diferente detiene el procedimiento: debe revisarse si cambió la versión publicada o si la descarga está incompleta, sin sustituir el original del proyecto.

También es posible descargar el SAV desde la ficha oficial, guardarlo en la ubicación de la tabla y ejecutar sin conexión:

```bash
python F1/src/convertir_enssex.py
```

El proceso informa su avance y termina con `Conversión verificada: 20392 filas y 1126 columnas.`. La evidencia queda en `F1/docs/verificacion_conversion_enssex.json`. Un código de salida distinto de cero indica que el procedimiento no se completó y requiere revisar el mensaje de error.

El script vuelve a generar y comprobar los resultados antes de aceptarlos. Si un CSV o archivo de metadatos existente tiene contenido diferente, se conserva intacto y se detiene la escritura de las salidas. Para revisar una diferencia se puede utilizar otra carpeta:

```bash
python F1/src/convertir_enssex.py --output-dir F1/data/raw/revision_conversion --report F1/data/raw/revision_conversion/verificacion_conversion_enssex.json
```

Este ejemplo utiliza el mismo SAV y deja las salidas de revisión separadas. El archivo de evidencia indicado con `--report` se actualiza en cada ejecución correcta. Todas las opciones están disponibles mediante `python F1/src/convertir_enssex.py --help`.

## Criterios de conversión

La lectura utiliza `pyreadstat.read_sav` con `apply_value_formats=False` y `user_missing=True`. Se conservan los códigos originales de respuesta, sin reemplazarlos por etiquetas ni convertir automáticamente los faltantes definidos por el usuario en SPSS. Sus definiciones se guardan en los metadatos; en esta versión, `missing_ranges` está vacío. Esto no significa que las preguntas carezcan de códigos de no respuesta.

El CSV se escribe con separador `;`, codificación `utf-8-sig`, punto decimal y sin agregar una columna de índice. Los campos se entrecomillan cuando su contenido lo requiere. Los faltantes se representan como campos vacíos y los formatos de fecha reconocidos por el lector se expresan como texto de fecha. Las etiquetas, las categorías, los formatos y las medidas originales se conservan en el archivo JSON complementario.

La interpretación analítica de las variables se determina con el cuestionario y el diccionario del estudio. La marca automática de SPSS y el tipo inferido al leer el CSV no sustituyen esa clasificación.

## Comprobaciones de integridad

El script vuelve a leer el CSV y verifica:

- Cantidad de registros y columnas, y nombres únicos de columnas.
- Conservación de los nombres y del orden de las columnas.
- Correspondencia de los valores numéricos y de sus faltantes, con tolerancia relativa de `1e-14` y tolerancia absoluta de cero.
- Coincidencia de textos y fechas con la representación exportada; la lectura de comprobación conserva como texto valores literales como `NA`.
- Cantidad de campos de cada registro CSV, respetando las comillas y los saltos de línea dentro de los campos.
- Conservación de la huella del SAV antes y después del procesamiento.

El 20/09/2026 se probó la descarga oficial y la conversión con el entorno del proyecto. El CSV regenerado tiene **51.201.111 bytes** y coincide byte por byte con la copia de trabajo anterior. Su huella SHA-256 es:

```text
75393ce321f5151fbfd7846034158aabcbe448e82c76fa7c919eeace194ef0d8
```

El [registro de verificación](verificacion_conversion_enssex.json) contiene los resultados y las versiones utilizadas. Esta comprobación respalda la conversión de formato; la validación del dataset analítico y la ejecución completa de los notebooks se documentarán durante el desarrollo de F2 y la verificación integral de reproducibilidad.

## Lectura desde los notebooks

Desde `F1/notebooks`:

```python
from pathlib import Path
import pandas as pd

ruta = Path("../data/raw/20241205_enssex_desde_sav.csv")
datos = pd.read_csv(ruta, sep=";", encoding="utf-8-sig")
```

Desde `F2/notebooks`, la ruta relativa es `../../F1/data/raw/20241205_enssex_desde_sav.csv`. En F2 se revisarán los tipos inferidos, los textos que pandas pueda interpretar como ausentes y los códigos especiales de cada variable antes de limpiar o transformar los datos.

## Fuente técnica

La configuración de lectura y los metadatos disponibles se describen en la [documentación oficial de pyreadstat](https://ofajardo.github.io/pyreadstat_documentation/_build/html/index.html). Las cantidades y huellas indicadas en esta guía proceden de la comprobación de los archivos del proyecto.
