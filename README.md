# MCDI500 · Grupo 9 · ENSSEX

Proyecto de Programación para la Ciencia de Datos de la Universidad Andrés Bello.

Nuestro proyecto utiliza ENSSEX 2022–2023 para abordar la siguiente pregunta:

> ¿Cómo varían la valoración de la vida sexual y el bienestar mental o emocional percibido según el grado de dependencia económica de la pareja entre las personas encuestadas en ENSSEX 2022–2023 que conviven con ella?

El alcance es descriptivo y comparativo de la muestra, sin ponderación. La definición incluye 12 variables principales y 3 auxiliares; las dos valoraciones se mantienen separadas y las diferencias no se interpretan como relaciones causales.

## Integrantes

- Guillermo Osorio Zamora — [gosoriozamora](https://github.com/gosoriozamora)
- Karla Patricia Pizarro Correa — [KarlaPPC](https://github.com/KarlaPPC)

## Organización del proyecto

En este repositorio reuniremos el trabajo de las fases 1 y 2 para la Sumativa 1. Mantendremos esta base para continuar después con las fases 3 y 4.

```text
proyecto-enssex/
├── README.md
├── requirements.txt
├── .gitignore
├── F1/
│   ├── README.md
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── notebooks/
│   ├── src/
│   └── docs/
├── F2/
│   ├── README.md
│   ├── notebooks/
│   └── docs/
├── F3/
├── F4/
└── docs/
```

- **F1:** definición del problema, objetivos, preparación del entorno y primera revisión de los datos.
- **F2:** obtención, exploración, limpieza, transformación y comprobación de los datos.
- **F3 y F4:** espacios reservados para las siguientes fases del curso.
- **docs, en la raíz:** informe integrado de la Sumativa 1 y sus anexos.

Las carpetas `F1/data` y `F1/src` se utilizarán también en las fases posteriores, siguiendo la organización de la guía del curso y de nuestro mapa conceptual. F2 guardará los datos que procese en `F1/data/processed`; el código y las explicaciones de esa fase estarán identificados en F2.

Conservamos una copia de la Formativa 1, sin cambios, en [F1/docs/Formativa1_Grupo9.pdf](F1/docs/Formativa1_Grupo9.pdf). El informe de la Sumativa 1 se preparará como un documento nuevo en [docs](docs/README.md).

El [notebook F1](F1/notebooks/F1_Definicion.ipynb) contiene la definición del proyecto, el diccionario, la comprobación del entorno y el reconocimiento inicial de la base. Se ejecutó completo desde un kernel nuevo en el equipo de Guillermo y conserva sus salidas. El notebook F2 y la integración final del informe siguen pendientes.

Los archivos `.gitkeep` permiten conservar en Git las carpetas que aún no tienen contenido. No forman parte del análisis.

## Instalación y ejecución

La [guía de instalación y ejecución](F1/docs/Instalacion_y_ejecucion.md) explica el procedimiento desde una copia nueva del repositorio: requisitos de Windows y Git Bash, Python 3.13.15 de 64 bits, creación de `.venv`, instalación de las versiones de `requirements.txt`, registro del kernel y ejecución de los notebooks.

Si el entorno ya está preparado, abrir Git Bash en la raíz del proyecto y ejecutar:

```bash
source .venv/Scripts/activate
python -m pip check
python -m jupyterlab
```

En JupyterLab se utiliza **Python (grupo9-mcdi500)**, cuyo identificador es `grupo9_mcdi500`. Cada integrante registra este kernel desde su propio entorno virtual.

Abrir `F1/notebooks/F1_Definicion.ipynb`, seleccionar el kernel del proyecto y utilizar **Kernel → Restart Kernel and Run All Cells**. Requiere el archivo `F1/data/raw/20241205_enssex_desde_sav.csv`, con separador `;` y codificación `utf-8-sig`. El archivo no se descarga al clonar el repositorio: los datos originales están excluidos de Git. La [guía de obtención y conversión de ENSSEX](F1/docs/Obtencion_y_conversion_ENSSEX.md) explica cómo descargarlos y reconstruir el CSV con `python F1/src/convertir_enssex.py --download`, desde la raíz del proyecto y con el entorno activo. El script conserva el SAV y verifica la integridad de la conversión; la [evidencia de ejecución](F1/docs/verificacion_conversion_enssex.json) registra sus resultados.

F1 comprueba las dependencias, la estructura, la identidad del CSV y la presencia de las 15 variables. Reconoce los 20.392 registros y las 1.126 columnas sin filtrar, limpiar, imputar ni recodificar. Sus tablas distinguen vacíos y códigos de no respuesta, y la comprobación final verifica que la base permanezca intacta. La validación preliminar se conserva como antecedente docente; no es necesario ejecutarla para correr F1. Cuando F2 esté disponible, se ejecutará después de F1.

El 20/09/2026 se comprobó en el equipo de Guillermo que las 121 dependencias registradas coinciden con las instaladas, que `pip check` no detecta conflictos y que el kernel apunta a `.venv`. La verificación integral de reproducibilidad sigue pendiente: comprenderá la instalación desde una copia nueva del repositorio y la ejecución completa del proyecto en ambos equipos.

La conversión de SAV a CSV requiere `pyreadstat==1.3.6`, incorporado a `requirements.txt`. Si el entorno se preparó antes de esta incorporación, actualizarlo con `python -m pip install -r requirements.txt` y comprobarlo con `python -m pip check`.

Se define `SEMILLA = 42` para las operaciones aleatorias que eventualmente se incorporen. F1 y la validación preliminar no utilizan aleatoriedad. Los datos y `.venv` se mantienen fuera del control de versiones; cada integrante reconstruye su entorno.

## Trabajo en equipo

Ambos integrantes guardaremos nuestros cambios desde nuestras propias cuentas de GitHub. Los mensajes de cada commit describirán el aporte realizado, para que podamos seguir el avance del trabajo y revisar los cambios.

## Trabajo pendiente

- Construir y ejecutar el notebook F2, conservando sus resultados.
- Repetir F1 en el equipo de Karla y realizar la verificación integral de ambos notebooks en los dos equipos.
- Armonizar el informe con la pregunta, los objetivos y las 15 variables documentadas en F1.
- Explicar las decisiones de limpieza y transformación.
- Probar el código con datos habituales y con situaciones que puedan producir errores.
- Revisar los resultados de cada etapa.
- Mantener actualizadas las dependencias y la guía de ejecución al completar los notebooks y el procedimiento de obtención de datos.
- Preparar el informe, relacionar el trabajo con el mapa conceptual e incorporar las referencias.
- Comprobar que el docente pueda acceder al repositorio.
