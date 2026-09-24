# Fase 1 · Definición y entorno

El [notebook F1_Definicion.ipynb](notebooks/F1_Definicion.ipynb) presenta el problema, la pregunta, los objetivos, el alcance y las variables del proyecto ENSSEX. Incluye el diccionario, la procedencia y licencia de los datos, las limitaciones y la continuidad prevista entre las fases.

## Reconocimiento inicial de los datos

El código está organizado en funciones para comprobar las dependencias, la estructura de carpetas, la identidad del CSV y la disponibilidad de las variables. Reconoce la base completa de 20.392 registros y 1.126 columnas y muestra el perfil de las 19 variables acordadas, distinguiendo campos vacíos y códigos de no respuesta.

La selección comprende 19 columnas originales: 3 variables centrales, 12 complementarias y 4 auxiliares. Incluye género (`p3`), año de inicio de convivencia (`p84`), edad de la pareja (`p91`) y `fecha` como referencia temporal por validar. Los años aproximados de convivencia y la diferencia de edad se calcularán en F2 cuando sus entradas estén validadas. El diagnóstico de F1 informa dos fechas de 1970 en la base completa; no corrige ni elimina esos registros.

F1 conserva todos los registros y columnas. La selección de convivientes, la limpieza, las recodificaciones y la exportación del conjunto procesado se realizarán en F2. La comprobación final confirma que el archivo y la tabla en memoria permanecen sin cambios.

## Cómo ejecutar F1

1. Seguir la [guía de instalación y ejecución](docs/Instalacion_y_ejecucion.md) para disponer del entorno y del kernel **Python (grupo9-mcdi500)**.
2. Obtener el CSV mediante la [guía de obtención y conversión](../docs/datos/Obtencion_y_conversion_ENSSEX.md). Los datos no se incluyen al clonar el repositorio.
3. Desde la raíz del proyecto, activar `.venv` e iniciar JupyterLab.
4. Abrir `F1/notebooks/F1_Definicion.ipynb` y seleccionar el kernel del proyecto.
5. Utilizar **Kernel → Restart Kernel and Run All Cells**, revisar las salidas y guardar el notebook.

La ejecución utiliza rutas relativas desde `F1/notebooks`. Requiere el CSV convertido en `data/raw` y la evidencia de conversión en `docs/datos/verificacion_conversion_enssex.json`.

## Organización de los archivos

- `notebooks`: notebook vigente de definición y reconocimiento de F1.
- `docs`: guías de entorno y evidencias de F1.
- `antecedentes`: validación preliminar y su informe, conservados como documentación histórica.
- Los originales compartidos están en `data/raw`, desde la raíz del proyecto; la conversión está en `src/convertir_enssex.py` y su documentación en `docs/datos`.
- La preparación, pruebas y productos de F2 están dentro de `F2`.

## Evidencia y continuidad

F1 se ejecutó completo desde un kernel nuevo en el equipo de Guillermo, con 10 celdas de código numeradas consecutivamente y sin errores. Las salidas registran 121 dependencias coincidentes, la comprobación de la base y tres casos de entrada incorrecta detectados. Falta reproducir el notebook completo en el equipo de Karla y realizar la verificación conjunta con F2.

El [notebook de validación preliminar](antecedentes/Validacion_preliminar_ENSSEX.ipynb) se conserva como antecedente del material del curso. Su clasificación automática debe contrastarse con el diccionario del equipo y no sustituye la interpretación analítica de las variables.
