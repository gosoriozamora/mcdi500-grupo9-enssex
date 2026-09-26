# Exportación y relectura de F3

El módulo `F3/src/exportacion_enssex.py` guarda los resultados de
`PipelineENSSEX` y verifica que pueden recuperarse. Separamos el cálculo en
memoria de la escritura para poder probarlos y utilizarlos por separado.
Son funciones, porque esta operación no necesita mantener estado entre llamadas.

## Archivos y representación

| Archivo | Contenido |
|---|---|
| `enssex_convivientes_F3.csv` | Tabla principal: 19 columnas originales preparadas y diferencia de edad. |
| `enssex_convivientes_F3_nominales.csv` | Folio e indicadores de las variables nominales. |
| `exportacion_F3.json` | Copia del esquema, nombres y orden de columnas, tipos, filas y huellas SHA-256 de los dos CSV. |

Los CSV usan separador `;`, UTF-8 con BOM, fechas `AAAA-MM-DD`, códigos enteros,
campos vacíos para faltantes y finales de línea LF. Las huellas corresponden a los
bytes exportados: una edición o conversión LF/CRLF del CSV invalida la huella.
Esto es distinto de la huella normalizada del código o esquema de F2.

CSV no conserva categorías ni tipos de pandas. `leer_resultados_f3()` usa el
manifiesto para restaurar enteros anulables, texto, fechas, categorías y su orden,
además de indicadores `uint8`. Comprueba los códigos antes de convertirlos a
categorías, para impedir que un valor desconocido se convierta silenciosamente
en un faltante. Los indicadores se comprueban antes de convertirlos a `uint8`.

No guardamos el índice de pandas: al leer se reconstruye un `RangeIndex` desde
cero. Conservamos el orden de las personas y su folio. Por eso la comparación
exacta usa `reset_index(drop=True)` sobre la tabla anterior a exportar; no
desactiva la comprobación de tipos, valores ni categorías.

## Uso

Después de cargar la base verificada y ejecutar el ejemplo de
[Pipeline_ENSSEX.md](Pipeline_ENSSEX.md), con `F2/src` y `F3/src` en la ruta
de importación:

```python
from exportacion_enssex import exportar_resultados_f3, leer_resultados_f3

destino = raiz / 'F3/data/processed'
evidencia = exportar_resultados_f3(resultados, destino, esquema)
recuperadas = leer_resultados_f3(destino)
print(recuperadas['principal'].shape)
print(recuperadas['nominales'].shape)
```

La primera función recibe el diccionario devuelto por el pipeline, un destino
y el mismo esquema. Antes de escribir vuelve a comprobar las invariantes de F2
y la correspondencia exacta de la matriz nominal. Escribe los tres archivos,
los relee y exige igualdad exacta con las tablas recibidas. Devuelve el manifiesto.
La segunda permite releer posteriormente la carpeta sin tener las tablas en memoria.

Con el conjunto real se recuperan 8.579 filas, 20 columnas principales y 65
nominales. No se realizan imputaciones ni se calcula duración de convivencia.
Los CSV de F2 y los datos originales no son destinos de esta operación.

## Repeticiones y límites

- Si cualquiera de los tres archivos de destino existe, la exportación se
  detiene antes de escribir. Para otra ejecución se usa otra carpeta, por ejemplo
  `F3/data/processed/segunda_ejecucion`, o se gestiona expresamente la versión anterior.
- La escritura no es una transacción: un corte del proceso o fallo de disco puede
  dejar archivos incompletos. En ese caso no se debe considerar terminada la
  exportación; la relectura debe finalizar correctamente. Se usa un destino nuevo
  para reintentar y se revisa el anterior antes de retirarlo.
- Las huellas permiten detectar cambios en los CSV respecto del manifiesto;
  no autentican quién lo creó ni reemplazan las comprobaciones del archivo fuente.
- La repetición byte a byte está probada en el mismo entorno. La reproducción
  entre equipos se comprueba usando las dependencias fijadas y estas pruebas.
- El notebook, las mediciones y la publicación de productos definitivos de F3
  se completarán en pasos posteriores.

## Validación

```bash
python F3/tests/validar_exportacion.py
```

La prueba utiliza `TemporaryDirectory`: no guarda productos permanentes.
Comprueba datos conocidos, faltantes, fechas, derivadas negativas, categorías
no observadas, una persona, folios textuales con ceros iniciales, rechazo de
sobrescritura y archivos alterados. También verifica categorías desconocidas
e indicadores fuera de 0/1, incluso después de recalcular la huella de prueba.
El caso de ceros iniciales verifica la serialización del texto recibido; no
modifica la normalización de folios que F2 realiza previamente.

En ENSSEX real verifica la igualdad exacta de ambas tablas, las 130
comprobaciones anteriores a exportar, dos exportaciones idénticas y las huellas
de los archivos originales y productos de F2 antes y después. Las tablas
recibidas se comparan con copias para verificar que permanecen intactas.
