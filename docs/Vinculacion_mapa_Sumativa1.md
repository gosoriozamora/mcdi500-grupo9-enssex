# Vinculación del mapa conceptual con el avance del proyecto

> Documento histórico de Sumativa 1. Las rutas y la arquitectura descritas corresponden a esa entrega. Para la versión actual, consultar [Organización del repositorio](Organizacion_repositorio.md); los archivos movidos conservan su antecedente en Git.

El mapa conceptual de la Formativa 1 orientó la organización del proyecto, el flujo de trabajo y la selección de herramientas. Su actualización conserva las seis etapas y los dos retornos iterativos, pero distingue lo implementado en F1 y F2 de los componentes previstos para F3 y F4. También incorpora las variables que sostienen la pregunta, el entorno virtual y las relaciones entre cada etapa y sus evidencias.

La pregunta actual es: «¿Cómo varían la valoración de la vida sexual y el bienestar mental o emocional percibido según el grado de dependencia económica de la pareja entre las personas encuestadas en ENSSEX 2022–2023 que conviven con ella?». Se aborda con un alcance descriptivo y comparativo de la muestra, sin ponderación ni atribución de relaciones causales.

La presentación contiene un mapa general y siete láminas de apoyo. El azul identifica componentes implementados en F1–F2; el verde, sus soportes transversales; el gris, componentes proyectados; y el ámbar, decisiones condicionadas a información adicional. Las flechas continuas indican relaciones o secuencia, y las discontinuas representan los retornos iterativos. La versión entregada en la Formativa se conserva como antecedente.

El [mapa actualizado en PDF](Mapa_conceptual_Sumativa1.pdf) y su [versión editable](Mapa_conceptual_Sumativa1.pptx) acompañan esta explicación. El [mapa de la Formativa 1](../F1/docs/Formativa1_Grupo9.pdf) se conserva sin cambios.

## Correspondencia entre planificación e implementación

| Elemento del mapa | Estado en la Sumativa 1 | Materialización y alcance | Evidencia concreta |
|---|---|---|---|
| Problemática y alcance | Implementado y delimitado | Pregunta centrada en dependencia y dos resultados percibidos; calidad de vida queda como complementaria. | [Notebook F1](../F1/notebooks/F1_Definicion.ipynb) |
| Dataset y fuente | Implementado | SAV verificado de ENSSEX: 20.392 registros y 1.126 columnas; original intacto. | [Obtención y conversión](../F1/docs/Obtencion_y_conversion_ENSSEX.md) |
| Indicadores de la pregunta | Implementado | Dependencia económica (p93), valoración de vida sexual (i_6_p9) y bienestar mental o emocional (i_2_p9), con sus escalas y códigos. | [Diccionario](../F2/docs/Diccionario_procesado_F2.md); [Justificación de las 19 columnas](../F2/docs/Seleccion_y_justificacion_variables_F2.md) |
| Selección de población y columnas | Implementado mediante código | Tiene pareja (p81=1) y convive (p83=1), conjuntamente: 8.579 personas. Lista declarada de 19 columnas, sin recorte manual. | [Funciones de preparación](../F1/src/preparar_enssex.py); [Esquema de variables](../F2/docs/esquema_variables_F2.json) |
| Definición y reconocimiento inicial | Implementado en F1 | Definición, objetivos, entorno y perfil inicial. F1 no limpia ni filtra la base. | [Notebook F1](../F1/notebooks/F1_Definicion.ipynb) |
| Adquisición y carga | Implementado | Descarga verificable y conversión íntegra SAV–CSV; carga antes de seleccionar el conjunto analítico. | [Script de conversión](../F1/src/convertir_enssex.py); [Notebook F2](../F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb) |
| Exploración de calidad | Implementado en F2 | Tipos, categorías, campos vacíos, no respuesta codificada, duplicados, extremos y denominadores. | [Notebook F2](../F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb); [Resultados de preparación](../F2/docs/Resultados_preparacion_F2.md) |
| Faltantes y saltos de pregunta | Implementado en el alcance seleccionado | Condiciones de pareja y convivencia previas al análisis; no se imputan vacíos fuera de aplicación. 883 códigos de no respuesta recodificados según pregunta; 0 imputaciones. | [Notebook F2](../F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb); [Bitácora](../F2/docs/Bitacora_decisiones_F1_F2.md) |
| Transformación de variables | Implementado | Ordinales con orden explícito; nominales sin orden; diferencia de edad calculada; sin escalamiento injustificado. | [Funciones de preparación](../F1/src/preparar_enssex.py); [Diccionario](../F2/docs/Diccionario_procesado_F2.md) |
| Duración de convivencia | Condicionada, no calculada | Se conserva una columna sin valores hasta validar qué evento representa fecha. Sus 8.579 ausencias son técnicas. | [Diccionario](../F2/docs/Diccionario_procesado_F2.md); [Bitácora](../F2/docs/Bitacora_decisiones_F1_F2.md) |
| Representación nominal auxiliar | Implementado | Siete nominales representadas con 64 indicadores y un folio. No amplía la selección conceptual de 19 variables ni implica un modelo entrenado. | [CSV nominal](../F1/data/processed/enssex_convivientes_F2_nominales.csv) |
| Validación técnica y exportación | Implementado en F2 | 130 invariantes, 21 casos controlados y relectura completa de ambos CSV. Esta validación precede al análisis sustantivo. | [Validación de F2](../F2/docs/validacion_F2.json); [Casos controlados](../F1/src/validar_preparacion_enssex.py) |
| Análisis por grupos | Proyectado para F3 | Comparar por separado ambas valoraciones según dependencia, declarar denominadores y revisar tamaños de grupos. | [Notebook F1](../F1/notebooks/F1_Definicion.ipynb); apartado de continuidad de [Notebook F2](../F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb) |
| Evaluación, interpretación y comunicación | Proyectado para F4 | Interpretar diferencias y limitaciones, comunicar resultados y revisar las decisiones si la evidencia lo requiere. | [Notebook F1](../F1/notebooks/F1_Definicion.ipynb); mapa actualizado, láminas 1 y 7 |
| Retorno de exploración a definición | Representado; revisable durante el proyecto | Permite ajustar pregunta, alcance o selección a la calidad y pertinencia de los datos. La evolución efectuada se explica en el apartado siguiente. | Mapa actualizado, láminas 1 y 7; [Bitácora](../F2/docs/Bitacora_decisiones_F1_F2.md) |
| Retorno de evaluación a preparación | Proyectado para F3–F4 | Si la interpretación detecta problemas, se revisan reglas de preparación, se justifica el cambio y se repite la validación. | Mapa actualizado, lámina 1; [Notebook F2](../F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb) como flujo reutilizable |
| Python, NumPy y pandas | Implementado | Operaciones tabulares y numéricas dentro de funciones reutilizables, con entradas y salidas comprobables. | [Funciones de preparación](../F1/src/preparar_enssex.py); [Pruebas de preparación](../F1/src/validar_preparacion_enssex.py) |
| JupyterLab y notebooks | Implementado | Integra código, explicación y salidas. F1 contiene 10 celdas de código y F2, 13. | [Notebook F1](../F1/notebooks/F1_Definicion.ipynb); [Notebook F2](../F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb) |
| Entorno virtual y versiones | Implementado | Cada equipo crea .venv con Python 3.13.15 y las 121 dependencias fijadas; el kernel usa ese intérprete. | [Instalación y ejecución](../F1/docs/Instalacion_y_ejecucion.md); [Dependencias](../requirements.txt) |
| Git y GitHub | Implementado | Historial de cambios y contribuciones identificables de ambos integrantes; archivos publicados para revisión. | Commits f6e89b9, a2719e7, f374a0f, d9de7f0 y 3e162f7 en el [historial](https://github.com/gosoriozamora/mcdi500-grupo9-enssex/commits/main/) |
| Reproducibilidad | Comprobada en el alcance documentado | Copia nueva, entorno nuevo, descarga oficial y ejecución independiente de F1/F2; CSV regenerados coincidentes al normalizar saltos de línea. | [Reproducción integral](../F1/docs/Verificacion_reproduccion_completa.md); [Ejecución de F2 por Karla](../F2/docs/Verificacion_F2_Karla.md) |
| Trazabilidad | Implementado | Folios para vincular registros, huellas para identificar archivos y commits para localizar cambios. Las celdas y la bitácora explican las razones. | [Validación de F2](../F2/docs/validacion_F2.json); [Bitácora](../F2/docs/Bitacora_decisiones_F1_F2.md); historial Git |
| Documentación científica | Implementado en notebooks y anexos | Narrativa previa al código, preguntas y respuestas del diccionario, alternativas descartadas y efectos medidos. Este documento reúne la vinculación para el informe. | [Notebook F1](../F1/notebooks/F1_Definicion.ipynb); [Notebook F2](../F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb); [Diccionario](../F2/docs/Diccionario_procesado_F2.md); [Bitácora](../F2/docs/Bitacora_decisiones_F1_F2.md) |
| Arquitectura y rutas compartidas | Implementado | F2 utiliza F1/data/raw, F1/data/processed y F1/src. Las rutas son relativas o se calculan desde la raíz del proyecto. | [README principal](../README.md); [Notebook F2](../F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb) |
| Archivos de gobierno | Implementado | README explica la ejecución; requirements fija dependencias; .gitignore excluye entorno y originales y permite los dos CSV procesados. | [README](../README.md); [requirements.txt](../requirements.txt); [.gitignore](../.gitignore) |

## Evolución de la planificación

### De una pregunta amplia a una comparación delimitada

La Formativa planteaba explorar la relación entre bienestar sexual, bienestar mental o emocional y calidad de vida en las personas adultas encuestadas. Durante la definición se precisó el fenómeno: comparar la valoración de la vida sexual y el bienestar mental o emocional percibido según la dependencia económica de la pareja entre quienes conviven con ella. La calidad de vida percibida (p8) se mantuvo como variable complementaria. Las dos valoraciones principales no se suman ni se tratan como diagnósticos clínicos.

Esta delimitación introdujo dos filtros conjuntos: «Tiene pareja actualmente» (p81=1) y «Convive actualmente con su pareja» (p83=1). El conjunto pasó de 20.392 a 8.579 personas por alcance de la investigación, no por eliminación de casos incompletos. Las 19 columnas originales se seleccionan mediante código: tres centrales, doce complementarias y cuatro auxiliares. Su utilidad se justifica individualmente en F1 y F2, sin asumir que todas entrarán juntas en un análisis posterior.

### De la preparación prevista a decisiones justificadas con cifras

Se mantuvo la decisión de regenerar el CSV desde el SAV tras los problemas de lectura de la descarga inicial. El procedimiento actual conserva el original, verifica su integridad y reconstruye la entrada mediante un script, evitando que la selección dependa de una edición manual.

La revisión de faltantes distingue condiciones de aplicación de la encuesta, no respuesta codificada y ausencias técnicas. En el cuestionario, la convivencia (p83), el ingreso relativo (p92), la dependencia económica (p93) y la actividad sexual con la pareja (p96) se aplican cuando existe pareja (p81=1); el año de inicio de convivencia (p84) se aplica cuando hay convivencia (p83=1). El filtro conjunto satisface estas condiciones. Los vacíos del resto de la base no se rellenan antes de seleccionar la población ni se clasifican todos como estructurales por su frecuencia.

En las 19 columnas seleccionadas se observaron cero campos físicamente vacíos antes de la limpieza. Se recodificaron 883 celdas de no respuesta según el diccionario de cada pregunta, conservando las 8.579 personas. No se imputaron respuestas ni se eliminaron filas por faltantes o extremos. La media, la mediana y la eliminación se evaluaron como alternativas sobre copias; se descartó aplicarlas para no atribuir respuestas no observadas y no reducir innecesariamente los casos disponibles. Cada comparación posterior deberá declarar sus denominadores.

Se calculó la diferencia entre la edad de la persona encuestada (p4) y la edad de su pareja (p91). En cambio, la duración de convivencia quedó reservada sin valores: el significado de la fecha registrada no permite establecer una referencia temporal validada. Esas 8.579 ausencias técnicas no son no respuestas del encuestado. El CSV principal tiene por ello 21 columnas, pero la selección sustantiva sigue siendo de 19 originales. La matriz nominal se conserva aparte, con 64 indicadores y un folio.

### Coherencia entre organización, herramientas y evidencias

Se conservó la arquitectura proyectada con datos y funciones compartidos dentro de F1. F2 lee el original desde F1/data/raw y exporta a F1/data/processed, con rutas relativas calculadas según la ubicación del notebook. La descarga del original se documenta como un paso reproducible; los dos CSV procesados y el diccionario sí se incluyen en GitHub. Esta decisión actualiza el ejemplo de commit de la Formativa, que anticipaba incorporar los originales al repositorio.

El entorno virtual se representa explícitamente y se relaciona con las dependencias y el kernel. La reproducibilidad se comprueba mediante la instalación y ejecución desde una copia nueva. La trazabilidad se apoya en folios, huellas e historial Git. La documentación explica las decisiones mediante celdas narrativas, diccionario y bitácora con motivos, alternativas e impactos. El commit identifica un cambio, pero su mensaje no sustituye la explicación metodológica.

### Continuidad del proceso

F1 aporta definición, entorno y reconocimiento inicial. F2 implementa la selección, preparación, transformación y validación técnica, con 130 invariantes y 21 casos controlados superados. El análisis sustantivo por grupos corresponde a las fases posteriores; los diagnósticos de calidad actuales no representan una respuesta final a la pregunta.

Se mantienen los retornos de exploración a definición y de evaluación a preparación. Permiten ajustar el alcance o revisar transformaciones cuando la evidencia lo requiera, documentar las razones, registrar el cambio y repetir las validaciones. La duración de convivencia permanece condicionada a validar la referencia temporal. Las técnicas posteriores se elegirán según la escala de las variables, los tamaños de los grupos y la pregunta, sin presuponer causalidad ni representatividad poblacional de resultados sin ponderar.

## Respuesta a la retroalimentación de la Formativa

| Observación recibida | Respuesta incorporada | Ubicación |
|---|---|---|
| Variables no declaradas | Cinco variables del núcleo con función y escalas; selección completa de 19 por roles y diccionario | Mapa, láminas 2 y 3; diccionario |
| Subconjunto debe generarse con código | Filtro conjunto y lista declarada aplicados a la base completa | Lámina 2; funciones y esquema |
| Principios separados del proceso | Conectores con verbos y evidencias por etapa | Láminas 1 y 6; tabla de vinculación |
| Falta entorno virtual | .venv relacionado con requirements y kernel | Lámina 5 |
| Colores sin significado declarado | Leyenda de cuatro colores y tipos de flecha | Lámina 1 |
| Nombre de fuente inconsistente | Uso uniforme de ENSSEX | Presentación completa |
| Distinguir faltantes estructurales y no respuesta | Condiciones del cuestionario, recodificación por pregunta y ausencia técnica separadas | Lámina 4; explicación de evolución |
| Rutas de F2 deben coincidir con el mapa | Carpetas compartidas F1/data y F1/src, documentadas y utilizadas | Lámina 5; README y notebook F2 |
| Conservar el proceso iterativo y la reflexión | Dos retornos y decisiones justificadas mediante cifras | Láminas 1 y 7 |

## Fuentes de la vinculación

La correspondencia se elaboró a partir del mapa original, la retroalimentación docente, la guía de desarrollo de la Sumativa 1 (apartado 4.14), la rúbrica de Canvas y las evidencias del repositorio hasta el commit `3e162f7`. Las condiciones de aplicación se contrastaron con el cuestionario ENSSEX, páginas 22–24. Los resultados cuantitativos proceden de las salidas de F2 y de su registro de validación.
