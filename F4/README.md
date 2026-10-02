# F4 Datos interpretables de ENSSEX

Preparamos la tabla que alimentará las visualizaciones de la pregunta de investigación. Esta primera tarea no calcula hallazgos ni genera figuras.

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

## Alcance del análisis posterior

Conservamos las dos valoraciones de bienestar por separado y el alcance descriptivo de la muestra, sin ponderación. Los denominadores y los gráficos se construirán en la siguiente tarea; la preparación no prueba una asociación ni implica significancia estadística o causalidad.
