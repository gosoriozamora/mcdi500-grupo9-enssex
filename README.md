# MCDI500 · Grupo 9 · ENSSEX

Proyecto de Programación para la Ciencia de Datos de la Universidad Andrés Bello.

Nuestro proyecto utiliza ENSSEX 2022–2023 para abordar la siguiente pregunta:

> ¿Cómo varían la valoración de la vida sexual y el bienestar mental o emocional percibido según el grado de dependencia económica de la pareja entre las personas encuestadas en ENSSEX 2022–2023 que conviven con ella?

El alcance es descriptivo y comparativo de la muestra, sin ponderación. La selección incluye 19 columnas originales: 3 variables centrales, 12 complementarias y 4 auxiliares. F2 calcula la diferencia de edad y reserva, sin valores, los años de convivencia hasta validar la referencia temporal. Las dos valoraciones se mantienen separadas y las diferencias no se interpretan como relaciones causales.

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

El [notebook F1](F1/notebooks/F1_Definicion.ipynb) contiene la definición del proyecto, el diccionario, la comprobación del entorno y el reconocimiento inicial de la base. Se ejecutó completo desde un kernel nuevo en el entorno local de desarrollo y conserva sus salidas. El [notebook F2](F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb) también está implementado: obtiene, explora, limpia, transforma, valida y exporta los datos. La integración final del informe sigue pendiente.

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

F1 comprueba las dependencias, la estructura, la identidad del CSV y la presencia de las 19 variables. Reconoce los 20.392 registros y las 1.126 columnas sin filtrar, limpiar, imputar ni recodificar. Sus tablas distinguen vacíos y códigos de no respuesta, y la comprobación final verifica que la base permanezca intacta. La validación preliminar se conserva como antecedente docente; no es necesario ejecutarla para correr F1. Después se ejecuta `F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb` con **Restart Kernel and Run All Cells**. F2 se inicia en un kernel independiente y lee el original; no depende de variables en memoria de F1.

El 20/09/2026 se comprobó en el entorno local de desarrollo que las 121 dependencias registradas coinciden con las instaladas, que `pip check` no detecta conflictos y que el kernel apunta a `.venv`.

La conversión de SAV a CSV requiere `pyreadstat==1.3.6`, incorporado a `requirements.txt`. Si el entorno se preparó antes de esta incorporación, actualizarlo con `python -m pip install -r requirements.txt` y comprobarlo con `python -m pip check`.

Se define `SEMILLA = 42` para las operaciones aleatorias que eventualmente se incorporen. F1, F2 y la validación preliminar no utilizan aleatoriedad. Los datos y `.venv` se mantienen fuera del control de versiones; cada integrante reconstruye su entorno.

## Preparación de F2 y resultados

F2 conserva 8.579 personas y convierte 883 códigos de no respuesta en ausencias, según cada pregunta. No imputa ni elimina filas por faltantes o extremos estadísticos. El archivo principal tiene 21 columnas: 19 originales preparadas, diferencia de edad calculada y duración de convivencia reservada sin valores. Las fuentes no definen el evento representado por `fecha`, por lo que no se presupone una fecha de entrevista.

Los archivos `enssex_convivientes_F2.csv` y `enssex_convivientes_F2_nominales.csv` se generan en `F1/data/processed`. La matriz auxiliar tiene 64 indicadores nominales más el folio. Ambos CSV se incluyen en el repositorio para facilitar su revisión y pueden reconstruirse ejecutando F2. El [diccionario de datos](F2/docs/Diccionario_procesado_F2.md) describe las preguntas, categorías y códigos. La relectura comprueba todos los valores y ausencias.

La [documentación de F2](F2/README.md) enlaza la bitácora, el diccionario, la configuración y los resultados. Las funciones de `F1/src/preparar_enssex.py` y sus casos controlados permiten revisar las decisiones y reproducir cada etapa. La duración reservada no debe incluirse en una selección global de casos completos.

## Trabajo en equipo

Ambos integrantes guardaremos nuestros cambios desde nuestras propias cuentas de GitHub. Los mensajes de cada commit describirán el aporte realizado, para que podamos seguir el avance del trabajo y revisar los cambios.

## Trabajo pendiente

- Revisar las salidas de F2 y registrar los cambios mediante el commit del integrante que realizó la ampliación.
- Mantener alineados el informe y los notebooks, utilizando como base las definiciones desarrolladas en el informe y contrastando las afirmaciones técnicas con las evidencias del repositorio.
- Integrar en el informe las decisiones y cifras generadas en [Resultados de preparación de F2](F2/docs/Resultados_preparacion_F2.md).
- Revisar conjuntamente los resultados de cada etapa y la limitación de la duración de convivencia.
- Mantener actualizadas las dependencias y la guía de ejecución al completar los notebooks y el procedimiento de obtención de datos.
- Preparar el informe, relacionar el trabajo con el mapa conceptual e incorporar las referencias.
- Comprobar que el docente pueda acceder al repositorio.

## Verificación integral de reproducción

Se comprobó una copia nueva de GitHub con un entorno virtual nuevo: las 121 dependencias, la obtención del original y ambos notebooks finalizaron correctamente. Los dos CSV regenerados coinciden con los publicados al normalizar los saltos de línea. Véase la [evidencia de reproducción](F1/docs/Verificacion_reproduccion_completa.md) y la [verificación de F2 por Karla](F2/docs/Verificacion_F2_Karla.md).

## Vinculación con el mapa conceptual

El [mapa actualizado en PDF](docs/Mapa_conceptual_Sumativa1.pdf) y su [versión editable](docs/Mapa_conceptual_Sumativa1.pptx) muestran la pregunta, las variables, el entorno y las conexiones entre etapas y evidencias. La [tabla de vinculación y evolución](docs/Vinculacion_mapa_Sumativa1.md) identifica qué está implementado, qué se proyecta para F3–F4 y por qué cambió la planificación. La Formativa original se conserva como antecedente.
