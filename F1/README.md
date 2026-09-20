# Fase 1 · Definición y entorno

El [notebook F1_Definicion.ipynb](notebooks/F1_Definicion.ipynb) presenta el problema, la pregunta, los objetivos, el alcance y las variables del proyecto ENSSEX. Incluye el diccionario, la procedencia y licencia de los datos, las limitaciones y la continuidad prevista entre las fases.

## Reconocimiento inicial de los datos

El código está organizado en funciones para comprobar las dependencias, la estructura de carpetas, la identidad del CSV y la disponibilidad de las variables. Reconoce la base completa de 20.392 registros y 1.126 columnas y muestra el perfil de las 15 variables acordadas, distinguiendo campos vacíos y códigos de no respuesta.

F1 conserva todos los registros y columnas. La selección de convivientes, la limpieza, las recodificaciones y la exportación del conjunto procesado se realizarán en F2. La comprobación final confirma que el archivo y la tabla en memoria permanecen sin cambios.

## Cómo ejecutar F1

1. Seguir la [guía de instalación y ejecución](docs/Instalacion_y_ejecucion.md) para disponer del entorno y del kernel **Python (grupo9-mcdi500)**.
2. Obtener el CSV mediante la [guía de obtención y conversión](docs/Obtencion_y_conversion_ENSSEX.md). Los datos no se incluyen al clonar el repositorio.
3. Desde la raíz del proyecto, activar `.venv` e iniciar JupyterLab.
4. Abrir `F1/notebooks/F1_Definicion.ipynb` y seleccionar el kernel del proyecto.
5. Utilizar **Kernel → Restart Kernel and Run All Cells**, revisar las salidas y guardar el notebook.

La ejecución utiliza rutas relativas desde `F1/notebooks`. Requiere el CSV convertido en `F1/data/raw` y la evidencia de conversión en `F1/docs/verificacion_conversion_enssex.json`.

## Organización de los archivos

- `notebooks`: F1 y la validación preliminar conservada como antecedente docente.
- `data/raw`: datos originales, CSV convertido y notas de procedencia.
- `data/processed`: resultados que generará F2 para las fases posteriores.
- `src`: código de conversión y funciones de apoyo compartidas por las fases.
- `docs`: guías, evidencias de conversión y entorno, y documentación del proyecto.

## Evidencia y continuidad

F1 se ejecutó completo desde un kernel nuevo en el equipo de Guillermo, con 10 celdas de código numeradas consecutivamente y sin errores. Las salidas registran 121 dependencias coincidentes, la comprobación de la base y tres casos de entrada incorrecta detectados. Falta reproducir el notebook completo en el equipo de Karla y realizar la verificación conjunta con F2.

El [notebook de validación preliminar](notebooks/Validacion_preliminar_ENSSEX.ipynb) se conserva como antecedente del material del curso. Su clasificación automática debe contrastarse con el diccionario del equipo y no sustituye la interpretación analítica de las variables.
