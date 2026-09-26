# Dos alternativas para calcular la diferencia de edad

Comparamos la resta `p4 - p91` mediante un bucle y mediante operaciones por
columnas. El signo distingue quién tiene mayor edad; no usamos valor absoluto.
La función `construir_derivadas` de F2 ya realiza la resta por columnas. El bucle
es una alternativa didáctica, no un defecto encontrado en el flujo existente.

## División funcional y vínculo con la clase

El notebook docente `S2_F3_NucleoAlgoritmico_Eficiencia_POO.ipynb`, sección 10,
define `con_bucle` y `vectorizada` para una misma operación y comprueba igualdad
antes de medir. Adaptamos ese procedimiento a una derivada real de ENSSEX.
Usamos funciones, un bucle `for`, una lista y una operación de pandas.

`F3/src/diferencia_edad.py` separa tres responsabilidades:

- `validar_edades`: comprobar columnas y tipos de entrada.
- `diferencia_con_bucle`: recorrer las dos columnas por posición y acumular restas.
- `diferencia_por_columnas`: restar directamente las dos series.

El flujo tiene etapas conocidas sobre tablas; no requiere recursividad.
La selección, limpieza y derivación de F2 permanecen como funciones; el pipeline
coordina esas funciones y los transformadores sin duplicar sus reglas.

## Contrato y alcance

Ambas alternativas reciben un DataFrame con columnas únicas y con `p4` y `p91`
de tipo nullable `Int64`, ya limpiadas y validadas con F2. No reciben códigos
crudos del SAV ni vuelven a decidir rangos de edades o códigos de no respuesta.
La validación compartida comprueba estructura y tipo, no sustituye la limpieza.

Devuelven una serie independiente llamada `diferencia_edad_pareja`, de tipo
`Int64`, con el mismo índice y orden. Si falta cualquiera de las edades, falta
también la diferencia. Admiten una tabla vacía con los tipos declarados y
conservan índices repetidos: no agrupan ni eliminan personas. No modifican la
entrada, no exportan datos y no cambian el pipeline principal.

La comparación utiliza el mismo contrato de salida en ambas funciones. En la
etapa de medición se deberá declarar si se incluye la validación común en el
intervalo medido y verificar de nuevo la igualdad para cada tamaño utilizado.

## Comprobación

Desde la raíz del proyecto, con el entorno activo:

```bash
python F3/tests/validar_diferencia_edad.py
```

La prueba controlada exige resultados conocidos: negativos, positivos, cero y
ausencias en una o ambas edades. Comprueba vacío, una fila, todas las diferencias
ausentes, índice desordenado y repetido, tipo y nombre. Verifica que modificar la
salida no modifica la entrada y rechaza columnas ausentes o duplicadas y tipos
incorrectos.

La prueba real carga el CSV original verificado, selecciona convivientes y limpia
con las reglas de F2. Ambas alternativas se comparan mediante
`pd.testing.assert_series_equal(..., check_exact=True)` con la derivada de F2
para las 8.579 personas, incluidos valores, faltantes, índice, nombre y tipo.

Estas pruebas acreditan equivalencia, no superioridad de rendimiento. Quedan
para la siguiente etapa los tamaños crecientes, las mediciones de tiempo y
memoria y la explicación de complejidad. Las muestras para medir no ampliarán
la población del estudio ni reemplazarán los productos de F2.
