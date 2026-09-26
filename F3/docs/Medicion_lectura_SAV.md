# Tiempo y memoria al leer ENSSEX

## Pregunta y alternativas

Para preparar F3 necesitamos 19 columnas del SAV original, que contiene 20.392
personas y 1.126 columnas. Comparamos dos funciones de `F3/src/medicion_lectura.py`:

- `leer_sav_completo`: lee todas las columnas y luego selecciona las 19.
- `leer_sav_columnas`: usa `usecols` para importar únicamente las 19 solicitadas.

Ambas devuelven una copia con las columnas en el orden del esquema y los mismos
metadatos relevantes. Usan `apply_value_formats=False` y `user_missing=True`,
como la conversión documentada de F2: conservamos códigos, no sustituimos por
etiquetas ni convertimos automáticamente los faltantes definidos por SPSS.

Antes de medir exigimos igualdad exacta de valores, tipos, ausencias, índices,
orden y metadatos: etiquetas de variables y valores, rangos de faltantes,
formatos originales, tipos de ReadStat y niveles de medición. No afirmamos
igualdad de todos los metadatos del SAV: solo de estos campos para las 19 variables.

Esta prueba corresponde a la **lectura anterior al filtro de convivencia**.
Por eso contiene 20.392 personas; las 8.579 personas se obtienen después.
No modifica todavía el cargador del pipeline, que sigue usando el CSV verificado
de F2. Incorporar la lectura directa exigiría revisar también esa integración.

## Método

El ejecutor `F3/benchmarks/medir_lectura_sav.py` verifica el SHA-256 del SAV contra
la evidencia de conversión antes de comenzar y comprueba que no cambie al final.
No descarga ni altera datos. La carga ocurre desde el mismo archivo local.

1. Ejecutamos ambas alternativas y comprobamos equivalencia fuera del cronómetro.
   Esto también calienta la caché del sistema: no medimos una lectura en frío.
2. Usamos `timeit.Timer(...).timeit(number=1)` en cinco repeticiones. Alternamos
   cuál función se mide primero y guardamos el orden. Cada tiempo total se divide
   por `number`; informamos el menor y conservamos todos los tiempos individuales.
3. El intervalo incluye lectura, selección y copia, extracción de metadatos y
   liberación del resultado temporal. Excluye importaciones, verificación SHA,
   comparación, impresión y escritura del informe de medición.
4. Hacemos `gc.collect()` antes de cada bloque. `timeit` desactiva temporalmente
   el recolector cíclico durante la medición, con su comportamiento predeterminado.
5. En una ejecución separada por alternativa medimos el máximo con `tracemalloc`.
   No cronometramos esa ejecución para evitar mezclar el costo del rastreo con
   los tiempos anteriores. También medimos la tabla final con
   `memory_usage(index=True, deep=True).sum()`.

**Las métricas de memoria son diferentes.** El máximo cuenta asignaciones rastreadas
durante la operación; no garantiza capturar toda la memoria nativa de ReadStat ni
representa la memoria total del proceso (RSS). El tamaño de la tabla final no
incluye metadatos ni tablas temporales. Se usa MiB: bytes divididos por 1.048.576.

Las verificaciones previas y las repeticiones utilizan cachés calientes. No
vaciamos cachés ni controlamos procesos de fondo. Alternar el orden reduce una
fuente de sesgo, pero no elimina las variaciones del equipo. Una única ejecución
de memoria por alternativa permite observar el máximo; no estima su variabilidad.

## Resultado observado

Evidencia completa: [medicion_lectura_SAV.json](medicion_lectura_SAV.json).
Ejecución del 26/09/2026, Windows 11 AMD64, Python 3.13.15, pandas 3.0.5,
numpy 2.5.3 y pyreadstat 1.3.6. El JSON registra procesador, huellas de código y
esquema normalizadas a LF, identidad del SAV, versiones, configuración y muestras.

| Alternativa | Menor tiempo por ejecución (s) | Máximo rastreado (MiB) | Tabla devuelta (MiB) |
|---|---:|---:|---:|
| SAV completo y selección | 1,408400 | 671,40 | 3,94 |
| Solo 19 columnas | 0,308359 | 13,15 | 3,94 |

Los tiempos por ejecución fueron:

- Completo: 1,408400; 1,455521; 1,457532; 1,445631; 1,455515 segundos.
- Solo columnas: 0,310903; 0,313731; 0,309332; 0,313180; 0,308359 segundos.

En esta ejecución, la relación entre los menores tiempos es aproximadamente
4,57: la lectura completa tarda 4,57 veces lo que tarda la selectiva. El tiempo
observado se reduce alrededor del 78,1 %. El máximo rastreado disminuye, aunque el
tamaño final coincide porque devolvemos la misma tabla. Estos resultados respaldan
preferir `usecols` cuando se necesite leer directamente estas variables del SAV;
no demuestran la misma aceleración del pipeline completo ni en cualquier equipo.

## Crecimiento y división funcional

Si hay `n` filas, `m` columnas originales y `k` columnas necesarias, materializar
la tabla completa demanda almacenamiento proporcional a `n*m`, además de la
selección. La tabla seleccionada demanda almacenamiento proporcional a `n*k`,
considerando ancho de datos comparable. Las columnas de texto también dependen
de la longitud de sus valores. Esta diferencia explica el costo de temporales.

No atribuimos al tiempo total de `usecols` una complejidad `O(n*k)`: el lector
puede necesitar recorrer y decodificar partes del archivo aunque no las entregue.
La medición usa un único tamaño de SAV y no prueba empíricamente una ley de
crecimiento. La comparación algorítmica con tamaños crecientes se hará por separado.

Dividimos responsabilidades en lectura, verificación de equivalencia, medición
y registro. Las dos funciones de lectura comparten las opciones y controles en
`_leer`; no duplicamos reglas. No usamos recursividad porque son pasos conocidos
sobre una tabla, sin una estructura de profundidad variable que recorrer.

## Reproducción y pruebas

Desde la raíz del repositorio, con el entorno del proyecto y el SAV original
obtenido según [la guía de datos](../../docs/datos/Obtencion_y_conversion_ENSSEX.md):

```bash
python F3/tests/validar_medicion_lectura.py
python F3/benchmarks/medir_lectura_sav.py --salida F3/benchmarks/resultados_locales/lectura_sav.json
```

Elegir un nombre diferente si ya existe: el ejecutor no sobrescribe mediciones.
Las cifras pueden variar; lo exigible es la equivalencia, la integridad del SAV
y el registro de condiciones. La evidencia publicada permanece como referencia.
Los resultados locales de revisión no se incluyen automáticamente en Git.

Las pruebas crean un SAV temporal pequeño con texto, un faltante de sistema y
un código definido como faltante en SPSS. Comprueban selección en otro orden,
valores, tipos y etiquetas, detección de diferencias, configuración inválida,
registro de repeticiones y protección de un rastreo de memoria externo. No se
afirma que una alternativa deba ganar en cualquier ejecución de prueba.

## Respaldo del método

- Material docente Semana 2: práctica, sección IV, y notebook de ejemplo F3,
  sección 10: separación de alternativas y medición de tiempo y memoria.
- [Python: timeit](https://docs.python.org/3/library/timeit.html): repeticiones,
  división por número de ejecuciones, mínimo observado y comportamiento del GC.
- [Python: tracemalloc](https://docs.python.org/3/library/tracemalloc.html):
  asignaciones rastreadas y medición del máximo.
- [pyreadstat: read_sav](https://ofajardo.github.io/pyreadstat_documentation/_build/html/index.html):
  selección de columnas, códigos y metadatos de SPSS.
