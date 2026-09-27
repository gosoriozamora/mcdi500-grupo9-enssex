# Reproducción de F3 desde una copia y un entorno nuevos

El 27 de septiembre de 2026 comprobamos F3 en Windows de 64 bits a partir de un clon nuevo de GitHub, commit `9294ac4d2895c7aaa9b23786eb23723c992818ff`. Creamos un entorno virtual independiente e instalamos las versiones de `requirements.txt`, sin acceso a los paquetes del entorno de trabajo.

La ejecución completa finalizó correctamente. El [registro estructurado](verificacion_reproduccion_F3.json) contiene entorno, huellas de entradas y productos, resultados de los siete scripts y huellas normalizadas del código utilizado.

## Procedimiento comprobado

1. Clonar el repositorio y registrar el commit recibido.
2. Crear una `.venv` nueva con Python 3.13.15, sin paquetes globales, e instalar `pip==26.2.1` y `requirements.txt`. La instalación puede utilizar la caché de distribuciones de pip; no se copió el entorno virtual anterior.
3. Comprobar las 121 versiones fijadas y ejecutar `python -m pip check`.
4. Ejecutar `python src/convertir_enssex.py --download` en el clon. Descargar nuevamente el SAV oficial y reconstruir el CSV; comparar ambas huellas con las publicadas.
5. Leer el notebook publicado, vaciar sus salidas solo en la copia de ejecución y ejecutar todas sus celdas mediante `nbclient`, con un kernel nuevo que apunta al intérprete de la nueva `.venv`.
6. Verificar los contadores consecutivos, ausencia de errores y salidas de error, resultados de pruebas, exportación y conservación de archivos de entrada.

El kernel se registró en un directorio aislado para esta comprobación; no se reemplazó el kernel habitual del proyecto. El notebook ejecutado y los registros completos se conservaron por separado. El notebook publicado por Karla permaneció intacto.

## Resultados

| Comprobación | Resultado |
|---|---|
| Python | 3.13.15, Windows de 64 bits |
| Dependencias fijadas | 121 versiones coincidentes |
| Compatibilidad de dependencias | `No broken requirements found.` |
| Originales | Descarga nueva; SAV y CSV coincidentes con sus huellas publicadas |
| Conversión | 20.392 filas y 1.126 columnas |
| Notebook | 16 celdas de código consecutivas, sin errores ni salidas `stderr` |
| Scripts de pruebas | 7 finalizados con código de salida 0 |
| Resultado principal | 8.579 personas y 20 columnas |
| Matriz nominal | 8.579 personas y 65 columnas |
| Comprobaciones del producto | 130 |
| Exportación | Dos CSV y manifiesto generados; relectura exacta |
| Integridad | Originales, módulos, productos F2 y notebook publicado intactos |

La ejecución del notebook quedó registrada entre `2026-09-27T15:24:53.655451+00:00` y `2026-09-27T15:25:31.844497+00:00`. Ese intervalo corresponde al notebook, no incluye la clonación, instalación ni descarga.

Los siete scripts ejecutados fueron `validar_transformadores.py`, `validar_faltantes.py`, `validar_pipeline.py`, `validar_exportacion.py`, `validar_medicion_lectura.py`, `validar_diferencia_edad.py` y `validar_medicion_algoritmos.py`, todos en `F3/tests`.

El notebook comprobó asimismo 883 códigos recodificados, cero imputaciones en el producto, 14 escenarios descriptivos de faltantes y equivalencia con F2. Las mediciones de lectura y diferencia de edad se repitieron en el entorno nuevo; sus tiempos son propios de esa ejecución y no sustituyen la evidencia histórica de `F3/docs`.

## Identidad de los productos generados

| Producto | SHA-256 |
|---|---|
| `enssex_convivientes_F3.csv` | `9af8b7f5f95289fdf1d632d60b384b5820013c659e184245f535ce11918a21fc` |
| `enssex_convivientes_F3_nominales.csv` | `8896ffa62fe569aed2d91f59560e88fff073ed2379790885bbdcf25be9fcb5f0` |

Los CSV y su manifiesto forman el paquete de exportación. Se regeneran localmente siguiendo el [README de F3](../README.md); este registro documenta su comprobación y no reemplaza esos archivos.

## Alcance

La prueba acredita la reproducción del código y notebook publicados en el commit indicado, con el entorno descrito y los originales verificados. No declara comprobada la instalación en macOS o Linux. La revisión cruzada del notebook consta en el PR #11; esta comprobación adicional usa un clon y un entorno virtual nuevos en el equipo de Guillermo.
