# F3 · Núcleo algorítmico de ENSSEX

Integramos las reglas de preparación de F2 mediante clases, funciones y estrategias intercambiables. Verificamos los resultados, comparamos tiempo y memoria, y exportamos productos cuya relectura recupera valores y tipos.

El punto de entrada es [F3_Nucleo_algoritmico_ENSSEX.ipynb](notebooks/F3_Nucleo_algoritmico_ENSSEX.ipynb). Contiene 36 celdas, de las cuales 16 son de código, con resultados guardados. Se incorporó mediante el [PR #11](https://github.com/gosoriozamora/mcdi500-grupo9-enssex/pull/11), después de su ejecución en el equipo de Karla y revisión de Guillermo.

## 1. Preparar el entorno y las entradas

Usar Windows de 64 bits y Git Bash, siguiendo la [guía de instalación](../F1/docs/Instalacion_y_ejecucion.md). Las versiones están fijadas en [requirements.txt](../requirements.txt); el entorno de referencia usa Python 3.13.15. No es necesario instalar dependencias adicionales para F3. Cada equipo crea su propio entorno virtual.

Desde la raíz del repositorio, con `.venv` preparado:

```bash
source .venv/Scripts/activate
python -m pip check
```

El notebook requiere estos archivos, además de los módulos publicados:

| Archivo | Función |
|---|---|
| `data/raw/20241205_enssex_data.sav` | Original para comparar lectura completa y por columnas |
| `data/raw/20241205_enssex_desde_sav.csv` | Base original convertida que utiliza la preparación |
| `docs/datos/verificacion_conversion_enssex.json` | Nombres y huellas esperadas de los originales |
| `F2/docs/esquema_variables_F2.json` | Variables, categorías y reglas de preparación |

Los dos primeros están excluidos de Git. Para obtenerlos si faltan:

```bash
python src/convertir_enssex.py --download
```

La [guía de obtención](../docs/datos/Obtencion_y_conversion_ENSSEX.md) describe fuente y conversión. No sustituir el CSV convertido por otro archivo con nombre parecido. Conservar las carpetas F2 y F3: reutilizamos funciones de F2 y las comparamos con los componentes de F3. No es necesario ejecutar antes los notebooks F1 y F2 ni compartir su kernel.

## 2. Ejecutar el notebook completo

Desde la raíz, con el entorno activo:

```bash
python -m jupyterlab
```

1. Abrir `F3/notebooks/F3_Nucleo_algoritmico_ENSSEX.ipynb`.
2. Seleccionar **Python (grupo9-mcdi500)**, cuyo identificador es `grupo9_mcdi500`.
3. Usar **Kernel → Restart Kernel and Run All Cells**.
4. Comprobar que las 16 celdas de código finalicen sin errores y que el cierre registre las validaciones correctas.
5. Guardar con **Ctrl + S** para conservar las salidas del equipo utilizado.

El notebook localiza la raíz del repositorio desde su ubicación, comprueba las entradas, muestra arquitectura y decisiones, ejecuta los siete scripts de pruebas, realiza mediciones y verifica la exportación. Los tiempos dependen del equipo; la corrección no exige obtener los mismos tiempos ni que una alternativa gane siempre. Al guardar una nueva ejecución pueden cambiar las salidas del notebook, aun cuando los datos resultantes coincidan.

Resultados esperados sobre la fuente verificada:

| Comprobación | Resultado |
|---|---|
| Base original | 20.392 filas y 1.126 columnas |
| Selección de convivientes | 8.579 personas y 19 columnas originales |
| Códigos de no respuesta recodificados | 883 |
| Producto principal | 8.579 × 20 |
| Matriz nominal auxiliar | 8.579 × 65 |
| Validación del producto | 130 comprobaciones |
| Imputaciones y exclusiones por faltantes en el producto | 0 |
| Estrategias descriptivas comparadas | 5 estrategias y 14 escenarios |

Las dos valoraciones de bienestar permanecen separadas. No calculamos duración de convivencia ni inferimos causalidad o representatividad nacional.

## 3. Productos locales y repetición de la ejecución

La variable `SALIDA_F3` apunta inicialmente a `F3/data/processed`. La exportación utiliza tres archivos:

```text
enssex_convivientes_F3.csv
enssex_convivientes_F3_nominales.csv
exportacion_F3.json
```

Los CSV contienen las tablas; el manifiesto registra esquema, tipos y huellas para verificar y reconstruirlas. Deben conservarse juntos si se trasladan los productos a otro equipo. El índice se reconstruye desde cero; el folio y el orden se conservan.

| Estado del destino | Comportamiento del notebook |
|---|---|
| No existe ninguno de los tres archivos | Exporta los tres y verifica la relectura exacta |
| Existen los tres | Comprueba huellas, esquema e igualdad con el resultado actual, sin sobrescribir |
| Solo existe una parte, o los archivos no pasan la verificación | Se detiene con error; revisar el destino antes de continuar |

Para conservar una exportación anterior y generar otra, se puede configurar `SALIDA_F3` con una carpeta nueva y vacía antes de ejecutar. No reutilizar un manifiesto con CSV de otra ejecución.

Los CSV de F3 y el manifiesto del destino predeterminado están excluidos de Git. Esto no impide ejecutar F3 en otro equipo: allí el notebook genera el conjunto completo desde sus entradas. Si se configura otro destino, revisar sus reglas de exclusión antes de incorporar cambios al repositorio. El notebook integrado conserva las salidas de validación, pero no sustituye los CSV si se necesita consumir las tablas exportadas. Revisar explícitamente qué archivos se incorporarán al repositorio; no añadir productos locales de forma indiscriminada.

La [documentación de exportación](docs/Exportacion_F3.md) explica las garantías y sus límites. Las huellas detectan alteraciones de los CSV; no autentican por sí solas el manifiesto.

## 4. Ejecutar las pruebas por separado

Desde la raíz, con el entorno activo:

```bash
python F3/tests/validar_transformadores.py
python F3/tests/validar_faltantes.py
python F3/tests/validar_pipeline.py
python F3/tests/validar_exportacion.py
python F3/tests/validar_medicion_lectura.py
python F3/tests/validar_diferencia_edad.py
python F3/tests/validar_medicion_algoritmos.py
```

Cada script debe finalizar sin excepciones. Cubren casos normales, límites, errores, copias independientes, control de estado, equivalencia con F2 y protección de originales. Las pruebas de exportación y de SAV sintético usan destinos temporales; estos comandos no reemplazan los productos definitivos de datos. El notebook ejecuta también los siete scripts y conserva sus salidas. Un mensaje de alcance de un script describe el componente que prueba, no la totalidad de F3.

## 5. Repetir las mediciones por separado

```bash
python F3/benchmarks/medir_lectura_sav.py --salida F3/benchmarks/resultados_locales/lectura_sav_revision.json
python F3/benchmarks/medir_diferencia_edad.py --salida F3/benchmarks/resultados_locales/diferencia_edad_revision.json
```

Elegir un nombre nuevo si el destino ya existe: los comandos rechazan sobrescrituras. El primero guarda JSON; el segundo guarda JSON y un gráfico PNG con el mismo nombre base. `resultados_locales` está excluido de Git. La evidencia histórica revisada está en [medición SAV](docs/medicion_lectura_SAV.json), [medición de diferencia de edad](docs/medicion_diferencia_edad.json) y su [gráfico](docs/medicion_diferencia_edad.png).

Se comprueba equivalencia antes de medir. `timeit` registra tiempos repetidos con orden alternado, y `tracemalloc` mide por separado el máximo de memoria rastreada. El tamaño de la tabla o serie devuelta es una métrica adicional. El rastreo no representa toda la memoria del proceso ni garantiza medir toda la memoria nativa de ReadStat.

El comando de diferencia de edad utiliza por defecto 1.000, 5.000, 20.000 y 50.000 filas. El notebook incorpora también 8.579. Son muestras con reemplazo y semilla 42 para evaluar rendimiento, incluso cuando el tamaño coincide con la selección real; no son participantes adicionales. La equivalencia frente a F2 sobre las personas reales se verifica por separado.

Ambas alternativas de diferencia de edad tienen tiempo O(n) y espacio O(n), incluyendo la salida. La curva de tiempos casi plana de la resta por columnas en el rango observado no implica O(1). Comparar la lectura del SAV tampoco demuestra una aceleración del pipeline completo, que mantiene su cargador original.

## 6. Arquitectura y evidencia

| Componente | Responsabilidad | Documentación |
|---|---|---|
| [transformadores.py](src/transformadores.py) | Contrato común, limpieza de códigos y tipificación | [Pipeline](docs/Pipeline_ENSSEX.md) |
| [faltantes.py](src/faltantes.py) | Estrategias intercambiables; conservación en el flujo principal | [Tratamiento de faltantes](docs/Tratamiento_faltantes.md) |
| [pipeline_enssex.py](src/pipeline_enssex.py) | Composición de etapas, derivada, matriz nominal y validación | [Pipeline](docs/Pipeline_ENSSEX.md) |
| [exportacion_enssex.py](src/exportacion_enssex.py) | Escritura y recuperación verificada de productos | [Exportación](docs/Exportacion_F3.md) |
| [diferencia_edad.py](src/diferencia_edad.py) | Dos algoritmos con el mismo contrato | [Alternativas](docs/Alternativas_diferencia_edad.md) |
| [medicion_algoritmos.py](src/medicion_algoritmos.py) | Comparación por tamaño con tiempo y memoria separados | [Complejidad](docs/Complejidad_diferencia_edad.md) |
| [medicion_lectura.py](src/medicion_lectura.py) | Lectura completa y por columnas del SAV | [Medición SAV](docs/Medicion_lectura_SAV.md) |

Usamos herencia en los transformadores, polimorfismo en sus llamadas comunes y encapsulamiento mediante configuración protegida, validación de estado y copias. `PipelineENSSEX` compone etapas y `TratamientoFaltantes` recibe funciones intercambiables para aplicar Strategy. Optamos por división funcional para el flujo tabular; no añadimos recursividad artificial.

El notebook presenta las decisiones y las referencias docentes, oficiales y académicas utilizadas. Las mediciones describen el entorno registrado; no son garantías de rendimiento para cualquier equipo.

## 7. Estado de reproducción

Los componentes se probaron en ambos equipos durante las revisiones. El notebook se ejecutó completo desde kernel nuevo y su contenido y resultados fueron revisados antes de integrar el PR #11. El 27/09/2026 se completó además la reproducción del commit `9294ac4` desde un clon nuevo, con una `.venv` independiente, 121 dependencias verificadas y una descarga nueva del SAV. Las 16 celdas, siete scripts y 130 comprobaciones finalizaron correctamente. Véase el [registro de reproducción de F3](docs/Verificacion_reproduccion_F3.md) y su [evidencia estructurada](docs/verificacion_reproduccion_F3.json).
