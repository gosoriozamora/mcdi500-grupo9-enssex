# F4 Análisis descriptivo y visualizaciones de ENSSEX

Preparamos una copia interpretable de los datos de F3 y calculamos tablas y tres figuras para responder la pregunta de investigación. Conservamos por separado la valoración de la vida sexual (`i_6_p9`) y el bienestar mental o emocional percibido (`i_2_p9`), comparados según la dependencia económica de la pareja (`p93`).

Profundizamos la comparación mediante sexo asignado al nacer (`p1`): cada figura de valoración incluye paneles Total, Hombre y Mujer, con denominadores propios y escala de color común. Conservamos las distribuciones generales como referencia. Esta desagregación no utiliza género declarado (`p3`) ni modifica la pregunta principal.

## Preparación

F3 debe haber generado juntos `enssex_convivientes_F3.csv`, `enssex_convivientes_F3_nominales.csv` y `exportacion_F3.json`, según [las instrucciones de F3](../F3/README.md). La matriz nominal es auxiliar; la tabla principal conserva los códigos categóricos originales. Su relectura restaura categorías, tipos y orden desde el manifiesto, comprobando también la equivalencia de la matriz nominal.

Con el entorno del proyecto activo, desde la raíz:

```bash
python F4/tests/validar_interpretables.py
python F4/src/datos_interpretables.py
```

El segundo comando lee `F3/data/processed` y escribe en `F4/data/processed`. Para conservar una salida anterior, elegir un destino nuevo:

```bash
python F4/src/datos_interpretables.py --salida F4/data/processed/segunda_ejecucion
```

El módulo exige que el destino no contenga sus dos archivos; no sobrescribe. Si una ejecución se interrumpe, revisar el destino parcial y reintentar en otro. Los CSV y JSON de esta carpeta permanecen locales, excluidos de Git; se regeneran mediante el código.

## Contenido y garantías

Se conserva la tabla principal completa: personas, folios, códigos, fechas, derivada, orden y ausencias. Cada variable categórica recibe una columna adicional `nombre__etiqueta`, con las etiquetas oficiales del esquema y el mismo orden nominal u ordinal. Los faltantes siguen siendo ausencias; no se convierten en categorías sustantivas ni se reemplazan por cero.

Los productos son `enssex_convivientes_F4_interpretable.csv` y `datos_interpretables_F4.json`. El CSV usa punto y coma, UTF-8 con BOM, fecha ISO, códigos enteros y campos vacíos para faltantes. El registro conserva tipos, categorías, esquema, huella del CSV y del manifiesto de origen y resultado de relectura. No es un registro de nuevos parámetros aprendidos: esta tarea solo aplica las etiquetas ya declaradas.

Para usarlo desde un notebook, incorporar `F2/src`, `F3/src` y `F4/src` a la ruta de importación y leer:

```python
from datos_interpretables import leer_interpretables

visual = leer_interpretables(raiz / 'F4/data/processed')
```

La lectura restaura tipos y categorías; verifica que cada etiqueta corresponda a su código. El CSV por sí solo no conserva los tipos de pandas. Debe mantenerse junto con su JSON.

Las pruebas cubren códigos y etiquetas conocidos, categorías no observadas, orden de 1 a 7, ausencia de respuestas, una persona, tabla vacía, conservación de las entradas y rechazo de códigos o etiquetas inconsistentes, folios duplicados, sobrescritura y archivos alterados. Las huellas detectan cambios respecto del registro, pero no autentican quién lo creó.

## Tablas y visualizaciones

Desde la raíz del repositorio, en Git Bash, activamos el entorno existente y ejecutamos:

```bash
source .venv/Scripts/activate
python -m pip check
PYTHONIOENCODING=utf-8 python F4/tests/validar_analisis.py
PYTHONIOENCODING=utf-8 python F4/src/analisis_descriptivo.py
```

El análisis lee por defecto los dos archivos de `F4/data/processed`. Si la copia interpretable se generó en otra carpeta, indicamos esa ubicación con `--entrada`. No es necesario ejecutar de nuevo F3 ni generar otra copia interpretable si ya contamos con entradas válidas.

El destino predeterminado es `F4/resultados_locales`, excluido de Git con todas sus subcarpetas. Para repetir una revisión conservando sus salidas previas, usamos un destino nuevo:

```bash
PYTHONIOENCODING=utf-8 python F4/src/analisis_descriptivo.py --salida F4/resultados_locales/revision_$(date +%Y%m%d_%H%M%S)
```

El módulo rechaza destinos que contengan archivos. Si la ejecución se interrumpe, conservamos la salida parcial y elegimos otra carpeta para el nuevo intento. El análisis no sobrescribe entradas ni salidas anteriores.

Los productos son:

- Ocho tablas CSV agregadas: cuatro generales (distribución de dependencia económica, denominadores y distribuciones de cada valoración) y cuatro equivalentes por sexo asignado al nacer (`p1`). Usan punto y coma y UTF-8 con BOM. Las columnas identificadoras de preguntas incluyen su descripción.
- Tres figuras en PNG y SVG: composición por dependencia económica de la pareja (`p93`), valoración de la vida sexual (`i_6_p9`) y bienestar mental o emocional percibido (`i_2_p9`). Las dos últimas incluyen paneles Total, Hombre y Mujer. Cada fila usa sus respuestas válidas y todos los paneles comparten la misma escala de color.
- `resumen_analitico.json`: cifras completas, criterios de cálculo, ausencias, versiones del entorno y huellas de entradas, código y productos. Los porcentajes no calculables se registran como `null`.

La carpeta [resultados](resultados/) conserva la ejecución seleccionada para revisión, con tablas agregadas y figuras que pueden publicarse. Los CSV con registros individuales y sus JSON siguen locales en `data/processed`; se mantiene el criterio acordado para esos datos. Las repeticiones locales no se incorporan automáticamente al repositorio.

## Denominadores e interpretación

La muestra tiene 8.579 personas. La dependencia económica de la pareja (`p93`) tiene 8.502 respuestas válidas y 77 ausencias. La comparación de valoración de la vida sexual (`i_6_p9`) usa 8.399 personas; la de bienestar mental o emocional percibido (`i_2_p9`), 8.491. Cada porcentaje se calcula entre las respuestas válidas del grupo correspondiente. No aplicamos eliminación global de filas, imputaciones ni cortes arbitrarios de la escala ordinal.

Sexo asignado al nacer (`p1`) registra 2.822 hombres y 5.757 mujeres, sin ausencias. Las bases de valoración de la vida sexual (`i_6_p9`) son 2.773 hombres y 5.626 mujeres; en bienestar mental o emocional percibido (`i_2_p9`), 2.791 y 5.700. Cada porcentaje desagregado usa su combinación de sexo y dependencia, no el total del sexo. Las tablas incluyen una sección Sin respuesta para auditar eventuales ausencias de sexo; actualmente sus conteos son cero y sus porcentajes no calculables. Esos casos siempre permanecerían en el panel Total.

El [análisis de resultados](docs/Resultados_descriptivos.md) presenta denominadores por grupo, interpretaciones, conexión con los objetivos y limitaciones. Las dos figuras de valoraciones muestran sus siete categorías y permiten distinguir patrones no uniformes entre grupos. No inferimos causalidad, significancia estadística ni resultados nacionales a partir de esta descripción sin ponderación.

Las pruebas nuevas usan casos pequeños con respuestas conocidas, ausencias superpuestas, sexo sin respuesta, grupos sin respuestas válidas y categorías con cero. Verifican la conciliación de los estratos con el total, la escala común de los gráficos, la conservación de entradas, la exportación repetible y el rechazo de sobrescrituras o entradas alteradas.

El notebook final integrador de F4, su ejecución de principio a fin, el informe y la presentación audiovisual siguen pendientes. Estos módulos y figuras constituyen su base analítica.
