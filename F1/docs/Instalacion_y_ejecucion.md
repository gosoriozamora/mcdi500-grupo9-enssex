# Instalación del entorno y ejecución del proyecto

Esta guía permite preparar el entorno del proyecto ENSSEX en Windows de 64 bits y ejecutar los notebooks disponibles. Los comandos se escriben en **Git Bash**, salvo los bloques identificados como Python, que corresponden a celdas del notebook.

La configuración de referencia se comprobó el 20 de septiembre de 2026. La instalación en un equipo nuevo necesita conexión para descargar Git, Python, el repositorio y las dependencias.

## 1. Herramientas y versiones de referencia

| Componente | Versión registrada | Uso |
|---|---|---|
| Python | 3.13.15, 64 bits | Ejecución del proyecto. |
| Git para Windows | 2.55.0.windows.5 | Control de versiones y Git Bash. |
| pip | 26.2.1 | Instalación y comprobación de dependencias. |
| NumPy | 2.5.3 | Operaciones numéricas. |
| pandas | 3.0.5 | Lectura y procesamiento tabular. |
| pyreadstat | 1.3.6 | Lectura del SAV y sus metadatos para la conversión. |
| SciPy | 1.18.1 | Herramientas científicas, según necesidad. |
| Matplotlib | 3.11.2 | Gráficos. |
| seaborn | 0.13.2 | Visualización estadística. |
| scikit-learn | 1.9.1 | Herramientas disponibles para fases posteriores; su instalación no implica que se entrene un modelo. |
| JupyterLab | 4.6.3 | Trabajo con notebooks. |
| ipykernel | 7.3.0 | Conexión entre Jupyter y el entorno del proyecto. |

Las versiones de las **121 dependencias** están fijadas en [requirements.txt](../../requirements.txt). Esta tabla resume las principales; el archivo es la referencia completa. Python y Git se instalan por separado y pip se registra aquí porque no está incluido en ese listado.

El archivo de dependencias corresponde a Windows e incluye paquetes propios de ese sistema, como `pywinpty`. Esta guía no declara comprobada la instalación en macOS o Linux.

## 2. Preparar Git y Python

Instalar Git para Windows desde la [página oficial de Git](https://git-scm.com/downloads/win) y abrir Git Bash. Instalar Python Install Manager desde el [sitio oficial de Python](https://www.python.org/downloads/), según las [instrucciones de Python para Windows](https://docs.python.org/3/using/windows.html). Después, cerrar y volver a abrir Git Bash para que reconozca los comandos.

Comprobar Git e instalar la versión de Python del proyecto si aún no está disponible:

```bash
git --version
py install 3.13.15
py -3.13 --version
py -3.13 -c "import struct; print(struct.calcsize('P') * 8)"
```

Los dos últimos resultados deben ser `Python 3.13.15` y `64`. Si Python 3.13.15 ya está instalado, basta con comprobarlo; no es necesario reinstalarlo. `py install` requiere el administrador de instalaciones de Python: el lanzador antiguo de Windows no ofrece ese comando. La versión de Git se registra como referencia, pero no se exige una coincidencia exacta para ejecutar los notebooks.

Si `py` no se reconoce, revisar la instalación del administrador y abrir una terminal nueva. Como alternativa, `python --version` permite comprobar un intérprete ya disponible: solo utilizarlo para crear el entorno si corresponde a Python 3.13.15 de 64 bits.

## 3. Obtener una copia del repositorio

Para un equipo que todavía no tenga la carpeta del proyecto:

```bash
mkdir -p ~/Proyectos
cd ~/Proyectos
git clone https://github.com/gosoriozamora/mcdi500-grupo9-enssex.git proyecto-enssex
cd proyecto-enssex
git rev-parse --short HEAD
```

El último comando muestra la revisión de código utilizada; registrarla cuando se realice la prueba de reproducción. Si GitHub solicita identificación, utilizar la cuenta con acceso al repositorio.

Si ya existe una copia del proyecto, abrir Git Bash en su carpeta raíz y conservar el trabajo que contenga. No es necesario clonarlo otra vez ni ejecutar los pasos de creación del entorno si este ya funciona.

## 4. Crear el entorno e instalar las dependencias

Desde la raíz del repositorio, en una copia que aún no tenga `.venv`:

```bash
py -3.13 -m venv .venv
source .venv/Scripts/activate
python --version
python -m pip install pip==26.2.1
python -m pip install -r requirements.txt
python -m pip check
```

El resultado esperado de la última instrucción es `No broken requirements found.`. Si existe un conflicto o falla la instalación de un paquete, corregirlo antes de continuar y registrar el mensaje. No actualizar todas las bibliotecas para intentar resolverlo sin revisar la diferencia con `requirements.txt`.

Cuando se use el intérprete alternativo comprobado en la sección «Preparar Git y Python» de esta guía, el comando de creación será `python -m venv .venv`. Una vez activado el entorno, utilizar `python -m pip` para instalar en ese mismo intérprete.

Comprobar el entorno y cargar las bibliotecas principales:

```bash
python -c "import sys, struct; print(sys.version); print(sys.executable); print('Entorno virtual:', sys.prefix != sys.base_prefix); print('Bits:', struct.calcsize('P') * 8)"
python -c "import numpy, pandas, scipy, matplotlib, seaborn, sklearn, jupyterlab, ipykernel, pyreadstat; print('Importaciones correctas')"
```

La ruta del intérprete debe terminar en `.venv/Scripts/python.exe` o su equivalente con barras de Windows; el entorno virtual debe indicar `True`. Cada integrante crea su propia `.venv`: no se copia de un equipo a otro ni se incorpora a Git.

## 5. Registrar el kernel del proyecto

Con `.venv` activo y desde la raíz del repositorio:

```bash
python -m ipykernel install --user --name grupo9_mcdi500 --display-name "Python (grupo9-mcdi500)"
python -m jupyter kernelspec list
```

La lista debe incluir `grupo9_mcdi500`. El nombre visible al abrir un notebook será **Python (grupo9-mcdi500)**. El registro se realiza en cada computador y apunta a su entorno local. Si se cambia la ubicación del proyecto, se debe reconstruir el entorno y registrar nuevamente el kernel desde esa ubicación.

## 6. Disponer del archivo de datos

La entrada de F1 y de la validación preliminar es:

```text
F1/data/raw/20241205_enssex_desde_sav.csv
```

Este archivo es el CSV convertido desde `20241205_enssex_data.sav`, con **separador punto y coma (`;`) y codificación `utf-8-sig`**. No sustituirlo por `20241205_enssex_data.csv`: el notebook está configurado para la copia convertida.

Los datos están excluidos de Git, por lo que clonar el repositorio no los incorpora. La [guía de obtención y conversión](Obtencion_y_conversion_ENSSEX.md) documenta la fuente, la licencia, la versión y las comprobaciones de integridad. Para descargar el SAV y generar el CSV y sus metadatos, ejecutar desde la raíz del repositorio, con `.venv` activo:

```bash
python F1/src/convertir_enssex.py --download
```

El comando requiere `pyreadstat==1.3.6`, incluido en el archivo de dependencias actualizado. Si el entorno se creó antes de incorporar esa biblioteca, volver a ejecutar `python -m pip install -r requirements.txt` y `python -m pip check`. La conversión conserva las filas, columnas y códigos originales; la preparación analítica corresponde a F2.

Desde la raíz del proyecto se puede comprobar que la entrada existe:

```bash
python -c "from pathlib import Path; p = Path('F1/data/raw/20241205_enssex_desde_sav.csv'); print(p); assert p.is_file(), 'Falta el CSV convertido en F1/data/raw'"
```

## 7. Abrir JupyterLab y ejecutar F1

Desde la raíz del repositorio, con `.venv` activo:

```bash
python -m jupyterlab
```

En JupyterLab:

1. Abrir `F1/notebooks/F1_Definicion.ipynb`.
2. Seleccionar el kernel **Python (grupo9-mcdi500)**.
3. Revisar la configuración: `RUTA_DATOS = Path("../data/raw/20241205_enssex_desde_sav.csv")`, `SEPARADOR = ";"` y `CODIFICACION = "utf-8-sig"`.
4. Seleccionar **Kernel → Restart Kernel and Run All Cells** y confirmar.
5. Comprobar que las 10 celdas de código tengan contadores consecutivos, sin errores, y que la tabla final muestre todas las comprobaciones en `OK`.
6. Guardar con `Ctrl + S` para conservar las salidas del equipo utilizado.

El notebook comprueba que el intérprete corresponda a la `.venv` del proyecto y que la carpeta de ejecución sea `F1/notebooks`. También contrasta todas las versiones de `requirements.txt` y la huella del CSV con `F1/docs/verificacion_conversion_enssex.json`. Si falta el CSV, seguir la guía de obtención y conversión; si una dependencia no coincide, actualizar el entorno antes de volver a ejecutar.

La salida esperada es una base de 20.392 filas y 1.126 columnas, con las 19 variables presentes y 121 dependencias coincidentes. Se muestran dimensiones, tipos de lectura, identificadores, vacíos y no respuesta codificada. F1 no filtra convivientes ni realiza limpieza, imputación o recodificación. Las comprobaciones finales verifican que el CSV y la tabla en memoria permanezcan intactos.

La selección comprende 19 columnas originales: 3 variables centrales, 12 complementarias y 4 auxiliares. Incluye género (`p3`), año de inicio de convivencia (`p84`), edad de la pareja (`p91`) y `fecha` como referencia temporal por validar. Los años aproximados de convivencia y la diferencia de edad se calcularán en F2 cuando sus entradas estén validadas. El diagnóstico de F1 informa dos fechas de 1970 en la base completa; no corrige ni elimina esos registros.

La evidencia de ejecución queda en las salidas del notebook. F1 no vuelve a escribir el informe del validador preliminar ni genera un dataset procesado. `Validacion_preliminar_ENSSEX.ipynb` se conserva como antecedente y no es un paso previo obligatorio para ejecutar F1.

## 8. Rutas relativas y orden de las fases

Las rutas de lectura y escritura se expresan desde la carpeta de ejecución del notebook, sin nombres de usuario ni rutas personales:

| Ubicación del notebook | Entrada original | Datos procesados | Documentación de su fase |
|---|---|---|---|
| `F1/notebooks` | `../data/raw/20241205_enssex_desde_sav.csv` | `../data/processed` | `../docs` |
| `F2/notebooks` | `../../F1/data/raw/20241205_enssex_desde_sav.csv` | `../../F1/data/processed` | `../docs` |

Ejemplo de lectura desde un notebook de F1:

```python
from pathlib import Path
import pandas as pd

ruta_datos = Path("../data/raw/20241205_enssex_desde_sav.csv")
assert ruta_datos.is_file(), "Revisar la ubicación del CSV y la carpeta de ejecución"
datos = pd.read_csv(
    ruta_datos, sep=";", encoding="utf-8-sig",
    keep_default_na=False, na_values=[""], low_memory=False,
)
```

Para F2 se utiliza la ruta de su fila en la tabla. F1 reconocerá los datos; el filtrado, la limpieza y las transformaciones corresponden a F2.

Los notebooks `F1/notebooks/F1_Definicion.ipynb` y `F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb` están desarrollados y conservan sus salidas. Ejecutar F1 y después F2, cada uno con **Kernel → Restart Kernel and Run All Cells** y el kernel **Python (grupo9-mcdi500)**. F2 no depende de variables en memoria de F1.

F2 importa sus funciones desde `F1/src`, verifica las dependencias y contrasta su selección con F1. Procesa 8.579 personas y genera dos archivos en `F1/data/processed`: el principal de 21 columnas y una matriz nominal auxiliar de 65 columnas. La diferencia de edad está calculada; los años de convivencia se conservan sin valores hasta validar la referencia temporal. No hay imputaciones ni eliminación de filas por faltantes o extremos.

Cada ejecución regenera la bitácora, el resumen para el informe, el diccionario y `validacion_F2.json` en `F2/docs`, además de actualizar `F2/README.md`. Al terminar, la tabla de cierre debe mostrar siete resultados OK. Estos resultados comprueban el procesamiento y no declaran resuelta la limitación temporal.

El código incluye casos normales, límites y excepciones, y verifica la relectura de ambos CSV. Guardar y cerrar el notebook antes de actualizar los archivos del repositorio; al recibir una versión nueva, volver a abrirlo desde disco antes de ejecutar.

## 9. Semilla y aleatoriedad

Se establece **`SEMILLA = 42`** como convención del proyecto. F1 declara esta constante, pero su lectura y reconocimiento inicial son deterministas y no utilizan operaciones aleatorias. F2 y la validación preliminar tampoco requieren aleatoriedad.

Si posteriormente se incorpora muestreo u otro procedimiento aleatorio, se declarará la semilla en la celda de configuración y se utilizará explícitamente en la operación. Para un generador de NumPy:

```python
import numpy as np

SEMILLA = 42
rng = np.random.default_rng(SEMILLA)
```

Las operaciones posteriores deberán usar ese generador; cuando una función reciba `random_state`, se le entregará `SEMILLA`. Se documentará para qué se usa y se conservarán las versiones de las bibliotecas. Declarar una constante sin conectarla a las operaciones aleatorias no asegura su reproducción. Este bloque es una pauta para el desarrollo posterior, no una transformación ya incorporada al notebook.

## 10. Retomar el trabajo y cerrar la sesión

Cada vez que se abra una terminal nueva, entrar en la raíz del proyecto y activar el entorno antes de iniciar JupyterLab:

```bash
cd ~/Proyectos/proyecto-enssex
source .venv/Scripts/activate
python -m jupyterlab
```

Si el repositorio se guardó en otra carpeta, abrir Git Bash directamente allí. Al terminar, guardar los notebooks, detener JupyterLab en la terminal con `Ctrl+C`, confirmar el cierre si se solicita y ejecutar `deactivate`.

## 11. Evidencias y límites de la comprobación actual

En el entorno local de desarrollo se verificaron el 20/09/2026:

- Python 3.13.15 de 64 bits en `.venv`.
- Las 121 versiones de `requirements.txt`, sin paquetes ausentes ni diferencias.
- `python -m pip check`, con resultado `No broken requirements found.`.
- La carga de NumPy, pandas, SciPy, ipykernel, JupyterLab y pyreadstat.
- El registro `grupo9_mcdi500`, cuyo intérprete coincide con el Python de `.venv`.
- La existencia de la entrada mediante las rutas relativas de F1 y F2.
- La ejecución completa de F1 desde un kernel nuevo, con 10 celdas de código consecutivas y sin errores.
- La lectura de 20.392 filas y 1.126 columnas y el perfil de las 19 variables acordadas.
- La detección de tablas vacías, columnas requeridas ausentes y nombres duplicados en ejemplos de control.
- La conservación del CSV y de la tabla en memoria al finalizar el reconocimiento.

El [registro de verificación del segundo entorno](verificacion_entorno_karla.md) documenta las comprobaciones de instalación realizadas.

La [verificación integral desde una copia nueva](Verificacion_reproduccion_completa.md) registra la revisión de Git, la instalación independiente, la ejecución de ambos notebooks y la coincidencia de los CSV publicados y regenerados. Si se incorporan nuevas dependencias, se revisará su necesidad, se actualizará `requirements.txt` desde el entorno del proyecto y se registrará el cambio; no se regenerará desde el Python general del computador.

## Fuentes técnicas

- [Entornos virtuales de Python](https://docs.python.org/3.13/library/venv.html).
- [Instalación de dependencias con pip](https://pip.pypa.io/en/stable/user_guide/#requirements-files).
- [Registro de kernels de IPython](https://ipython.readthedocs.io/en/stable/install/kernel_install.html).
- [Inicio de JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/starting.html).
- [Generadores aleatorios de NumPy](https://numpy.org/doc/stable/reference/random/generator.html).

Las versiones y rutas del proyecto proceden de la comprobación local; los enlaces técnicos respaldan los procedimientos generales.
