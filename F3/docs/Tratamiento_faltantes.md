# Tratamiento de faltantes en F3

El flujo principal conserva todas las personas y ausencias, siguiendo F2.
`TratamientoFaltantes` organiza escenarios descriptivos para las tres variables
centrales. Las imputaciones son simulaciones numéricas; no son nuevas respuestas
de la encuesta y no alimentan el CSV definitivo.

## Diseño y uso

La clase hereda de `Transformador`. Recibe una de cinco funciones con la misma
interfaz `(serie, elegibles, grupos)`: esto permite cambiar la estrategia sin
reescribir la clase. Cada objeto conserva copias de las reglas y de las columnas
originales necesarias, valida su estado y devuelve una copia de su resumen.

La entrada es la selección ya limpiada con F2, antes de convertirla a categorías.
Se necesita también la selección original, con su índice y códigos de no respuesta.
El objeto comprueba la correspondencia de la variable y, cuando corresponde, del
grupo. Para otra selección se construye otro objeto. `ajustar()` valida la entrada;
las estadísticas se calculan en `transformar()` sobre esa misma muestra. No es un
modelo de entrenamiento y predicción para datos nuevos.

Con `F2/src` y `F3/src` en la ruta de importación, y las tablas ya cargadas:

```python
from faltantes import TratamientoFaltantes, conservar_faltantes

tratamiento = TratamientoFaltantes(
    esquema, 'i_6_p9', conservar_faltantes, seleccion
)
resultado = tratamiento.ajustar(limpia).transformar(limpia)
resumen = tratamiento.resumen()
```

| Estrategia | Efecto y restricción |
|---|---|
| `conservar_faltantes` | Copia exacta de la tabla, incluidos tipos y ausencias. |
| `casos_disponibles` | Conserva filas con respuesta en la variable elegida, solo para ese cálculo. No equivale a casos completos de las 19 columnas ni garantiza disponibilidad del grupo. |
| `media_global` | Simula reemplazos por la media de los códigos observados, solo en celdas elegibles. |
| `mediana_global` | Simula reemplazos por la mediana; puede producir fracciones y no se redondea. |
| `mediana_por_dependencia` | Usa la mediana dentro de `p93`; no se aplica a la propia `p93`. Sin grupo o sin respuestas válidas en él, la ausencia permanece. |

Solo son elegibles para reemplazo los códigos explícitos de no respuesta de la
variable en la selección original. Los vacíos originales se protegen porque su
causa no se puede deducir de la tabla limpia. No se afirma que todo vacío sea
estructural. Este componente no se extiende automáticamente a otras preguntas
con saltos del cuestionario, a variables nominales, fechas o identificadores.

Las simulaciones de media y mediana convierten únicamente la variable elegida a
`Float64`. El resumen cuenta valores fuera de las categorías y fraccionarios:
no deben tipificarse ni tratarse como respuestas ordinales observadas. La varianza
de códigos es un diagnóstico mecánico, no evidencia de intervalos iguales en la
escala. Cuando la varianza original es cero o no se puede calcular, su cambio
porcentual se informa como ausente, no como cero.

Para comparar dependencia y bienestar deben declararse además los casos con ambas
respuestas disponibles, como en `disponibilidad_analisis()` de F2. El denominador
de `casos_disponibles` aquí corresponde solo a la variable elegida.

## Validación

Desde la raíz del repositorio, con el entorno del proyecto:

```bash
python F3/tests/validar_transformadores.py
python F3/tests/validar_faltantes.py
```

Las pruebas de faltantes cubren resultados conocidos, fracciones, vacíos protegidos,
ausencia de grupo o de donantes, una fila, ausencia total de respuestas, entradas
incorrectas, copias independientes, estado del objeto y recuperación tras un error.
La prueba real compara valores y resúmenes de los 14 escenarios con F2 para
8.579 personas y 19 columnas. En las tres centrales de esta selección no hay vacíos
originales; por eso la restricción adicional reproduce los resultados de F2.
Las pruebas no generan ni reemplazan archivos de datos.

Este componente todavía no incorpora el pipeline completo, mediciones ni notebook
F3. La referencia de comportamiento es `F2/src/preparar_enssex.py`, función
`comparar_imputaciones`, junto con `F2/docs/esquema_variables_F2.json`.
