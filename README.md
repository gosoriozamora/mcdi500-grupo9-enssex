# MCDI500 · Grupo 9 · ENSSEX

Proyecto de Programación para la Ciencia de Datos de la Universidad Andrés Bello.

Nuestro proyecto utiliza ENSSEX 2022–2023 para abordar la siguiente pregunta:

> ¿Cómo varían la valoración de la vida sexual y el bienestar mental o emocional percibido según el grado de dependencia económica de la pareja entre las personas encuestadas en ENSSEX 2022–2023 que conviven con ella?

El alcance es descriptivo y comparativo de la muestra, sin ponderación. Seleccionamos 19 columnas originales: 3 variables centrales, 12 complementarias y 4 auxiliares. F2 y F3 conservan 8.579 personas y agregan la diferencia de edad, con **20 columnas principales**. No calculamos duración de convivencia porque la referencia temporal no está validada. Las dos valoraciones se mantienen separadas; no interpretamos las diferencias como relaciones causales ni extrapolamos los resultados a todo Chile.

## Integrantes

- Guillermo Osorio Zamora — [gosoriozamora](https://github.com/gosoriozamora)
- Karla Patricia Pizarro Correa — [KarlaPPC](https://github.com/KarlaPPC)

## Organización y notebooks

| Fase | Contenido | Punto de entrada |
|---|---|---|
| F1 | Problema, objetivos, entorno y reconocimiento de la base | [Notebook F1](F1/notebooks/F1_Definicion.ipynb) |
| F2 | Exploración, limpieza, transformación y validación | [Notebook F2](F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb) y [documentación](F2/README.md) |
| F3 | Preparación mediante clases, estrategias, equivalencia con F2, eficiencia y exportación verificada | [Notebook F3 ejecutado](F3/notebooks/F3_Nucleo_algoritmico_ENSSEX.ipynb) e [instrucciones de F3](F3/README.md) |
| F4 | Carpeta reservada para la fase posterior | Sin implementación en esta entrega |

```text
proyecto-enssex/
├── README.md
├── requirements.txt
├── data/raw/                 # Originales compartidos, excluidos de Git
├── src/convertir_enssex.py   # Obtención y conversión de la fuente
├── F1/                     # Notebook, documentación y antecedentes
├── F2/                     # Notebook, módulos, pruebas y productos publicados
├── F3/
│   ├── README.md
│   ├── notebooks/           # Ejecución integrada y salidas
│   ├── src/                 # Clases, exportación, algoritmos y mediciones
│   ├── tests/               # Siete scripts de validación
│   ├── benchmarks/          # Mediciones reproducibles
│   ├── docs/                # Decisiones y evidencia técnica
│   └── data/processed/      # Productos generados localmente al ejecutar F3
├── F4/
└── docs/                   # Antecedentes de S1 y evidencia de conversión
```

Los originales se comparten entre fases. F3 reutiliza las reglas de `F2/src/preparar_enssex.py`; por eso debe conservarse la estructura del repositorio. La [organización inicial](docs/Organizacion_repositorio.md), la [Formativa 1 original](F1/docs/Formativa1_Grupo9.pdf), el [mapa conceptual de S1](docs/Mapa_conceptual_Sumativa1.pdf), su [versión editable](docs/Mapa_conceptual_Sumativa1.pptx) y su [tabla de vinculación](docs/Vinculacion_mapa_Sumativa1.md) se conservan como antecedentes de esa etapa.

## Instalación y ejecución

La [guía de instalación](F1/docs/Instalacion_y_ejecucion.md) describe Windows de 64 bits, Git Bash, Python 3.13.15, creación de `.venv`, instalación de [requirements.txt](requirements.txt) y registro del kernel. Las dependencias corresponden a Windows; no declaramos comprobada su instalación en otros sistemas.

Con el entorno preparado, desde la raíz del repositorio en Git Bash:

```bash
source .venv/Scripts/activate
python -m pip check
python -m jupyterlab
```

Seleccionar **Python (grupo9-mcdi500)**, identificador `grupo9_mcdi500`. Abrir el notebook de la fase, usar **Kernel → Restart Kernel and Run All Cells** y guardar al finalizar. Cada fase lee su entrada desde disco y no depende de variables en memoria de un notebook anterior.

Clonar el repositorio no descarga los originales. Para obtener el SAV y reconstruir el CSV, con el entorno activo:

```bash
python src/convertir_enssex.py --download
```

Consultar la [guía de obtención y conversión](docs/datos/Obtencion_y_conversion_ENSSEX.md) y su [evidencia](docs/datos/verificacion_conversion_enssex.json). F3 necesita **el SAV y el CSV convertido**: este último alimenta la preparación y el SAV se utiliza en la comparación de lectura. El CSV usa separador `;` y codificación `utf-8-sig`.

El [README de F3](F3/README.md) detalla entradas, ejecución, pruebas, mediciones, productos y cómo repetir el notebook cuando ya existen exportaciones.

## Resultados y decisiones de preparación

La base original contiene 20.392 registros y 1.126 columnas. La selección `p81 = 1` y `p83 = 1` conserva 8.579 personas. Se recodifican 883 códigos de no respuesta como ausencias, según el esquema. No se imputan valores ni se eliminan filas por faltantes o extremos estadísticos.

El producto principal tiene 19 columnas originales preparadas y una diferencia de edad calculada. La matriz auxiliar tiene **65 columnas: el folio y 64 indicadores nominales**. La duración de convivencia no forma parte de los productos: las fuentes no definen el evento representado por `fecha` y no presuponemos una fecha de entrevista.

Los dos CSV de F2 están publicados en `F2/data/processed` y pueden reconstruirse con su notebook. El [diccionario de F2](F2/docs/Diccionario_procesado_F2.md) describe preguntas, categorías y códigos. F3 verifica equivalencia exacta con F2 y exporta sus propios archivos, sin reemplazar los de F2. Sus CSV y manifiesto se generan juntos localmente; el notebook publicado conserva la evidencia de ejecución.

F3 compara cinco estrategias de faltantes en 14 escenarios, sin trasladar las imputaciones exploratorias al producto definitivo. Compara además lectura SAV completa frente a selección de columnas, y bucle frente a resta por columnas para la diferencia de edad. Usa `timeit` y `tracemalloc` en ejecuciones separadas. Ambas alternativas de diferencia de edad tienen complejidad temporal y espacial O(n), incluyendo la salida; los tiempos observados no cambian esa conclusión.

La semilla 42 se utiliza en las muestras con reemplazo de las mediciones algorítmicas. Estas muestras sirven para evaluar rendimiento; no amplían la población del estudio. F1, F2 y la preparación principal de F3 no requieren aleatoriedad.

## Revisión y reproducción

Trabajamos con ramas por tarea y revisión cruzada mediante pull requests. El [PR #11](https://github.com/gosoriozamora/mcdi500-grupo9-enssex/pull/11) incorporó el notebook ejecutado por Karla y revisado por Guillermo; el commit de integración es `9294ac4`.

Para F1 y F2 se documentó una [reproducción desde copia y entorno nuevos](F1/docs/Verificacion_reproduccion_completa.md), además de la [verificación de F2 por Karla](F2/docs/Verificacion_F2_Karla.md). Para F3 se dispone de pruebas de componentes en ambos equipos, ejecución completa del notebook desde kernel nuevo y revisión de sus resultados. El 27/09/2026 se comprobó también F3 desde un clon nuevo y una `.venv` independiente, con descarga nueva del SAV, 121 dependencias coincidentes, siete scripts y 130 comprobaciones correctas. Véase la [evidencia de reproducción de F3](F3/docs/Verificacion_reproduccion_F3.md).

La auditoría completa de Sumativa 2 y el informe institucional también permanecen pendientes. Las salidas técnicas y las revisiones de código no sustituyen la revisión de todos los criterios ni acreditan el envío de la evaluación.
