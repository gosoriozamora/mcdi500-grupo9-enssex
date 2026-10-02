# Verificación de tablas y figuras de F4

El 2 de octubre de 2026 ejecutamos en el equipo de Guillermo las pruebas del análisis y la generación sobre las 8.579 personas de la copia interpretable. Esta evidencia corresponde al trabajo local preparado para revisión; no acredita una ejecución de Karla ni la ejecución del notebook final integrador.

## Comprobaciones ejecutadas

- Pruebas previas de la copia interpretable: etiquetas, categorías, ausencias, relectura y detección de alteraciones.
- Pruebas nuevas del análisis: ocho personas con conteos calculados manualmente, ausencias superpuestas, distintas bases por dimensión, categorías sin observaciones y grupos sin base.
- Desagregación por sexo asignado al nacer (`p1`): denominadores propios de cada estrato, ausencias de sexo conservadas en el total y reconstrucción exacta de cada conteo general desde los estratos.
- Conservación de la tabla de entrada, sus tipos y categorías; rechazo de folios duplicados, categorías ajenas al esquema y orden incorrecto.
- Correspondencia de los porcentajes representados con las tablas y escala común en las dos figuras de valoraciones.
- Dos exportaciones del caso controlado con tablas e imágenes idénticas por huella; lectura de los CSV y JSON producidos.
- Rechazo de sobrescritura y detección de alteraciones en el CSV de entrada.
- Ejecución sobre datos reales, contrastada con el cálculo exploratorio anterior y una tabla cruzada independiente. Las 42 frecuencias de las dos valoraciones coinciden.
- Contraste de las 84 frecuencias desagregadas con un cruce independiente de sexo asignado al nacer (`p1`), dependencia económica de la pareja (`p93`) y cada valoración. Los cuatro CSV generales conservan exactamente sus valores y contenido tras agregar la desagregación.
- CSV interpretable y JSON de entrada con huellas iguales antes y después del análisis.
- Inspección visual de las tres figuras exportadas: títulos, categorías, porcentajes, ausencias, fuente y legibilidad.

Las comprobaciones finalizaron correctamente. Las instrucciones para reproducirlas están en el [README de F4](../README.md); las pruebas automatizadas se encuentran en [validar_analisis.py](../tests/validar_analisis.py).

## Resultados de control

| Elemento | Resultado |
| --- | ---: |
| Personas de la copia interpretable | 8.579 |
| Dependencia económica de la pareja (`p93`): respuestas válidas | 8.502 |
| Valoración de la vida sexual (`i_6_p9`): base de comparación | 8.399 |
| Bienestar mental o emocional percibido (`i_2_p9`): base de comparación | 8.491 |
| Personas con las tres respuestas válidas | 8.392 |
| Sexo asignado al nacer (`p1`): hombres / mujeres / ausentes | 2.822 / 5.757 / 0 |
| Valoración de la vida sexual (`i_6_p9`): base hombres / mujeres | 2.773 / 5.626 |
| Bienestar mental o emocional percibido (`i_2_p9`): base hombres / mujeres | 2.791 / 5.700 |

El registro [resumen_analitico.json](../resultados/resumen_analitico.json) conserva cifras sin redondear, criterios de denominadores, versiones del entorno y huellas SHA-256 de las entradas, módulos de preparación y análisis, tablas y figuras. Permite identificar los archivos concretos usados y producidos; las huellas no autentican por sí solas la autoría.

Python 3.13.15, pandas 3.0.5, NumPy 2.5.3 y Matplotlib 3.11.2 corresponden a esta ejecución. Los tiempos de pruebas o generación no se interpretan como una medición de eficiencia algorítmica.
