# Verificación integral de reproducción

Se verificó la revisión `d9de7f097fd3b0c1d975ed5d855f629c48c6a055` desde una copia nueva de GitHub, con un entorno virtual nuevo de Python 3.13.15 en Windows de 64 bits. Las 121 dependencias coincidieron con las versiones fijadas y `pip check` confirmó que no existen conflictos. Se descargó el SAV desde la fuente oficial y se generó el CSV siguiendo las instrucciones del proyecto. No se reutilizaron el entorno virtual ni los datos originales de la copia de desarrollo.

F1 y F2 se ejecutaron desde kernels nuevos e independientes, con 10 y 13 celdas de código respectivamente, sin errores. Se superaron 130 invariantes y 21 casos controlados. La base original de 20.392 registros y 1.126 columnas permaneció intacta.

Los dos CSV regenerados coincidieron con los publicados: el principal contiene 8.579 filas y 21 columnas; la matriz nominal, 8.579 filas y 65 columnas. La comparación mediante SHA-256 normalizó exclusivamente los saltos de línea CRLF a LF para evitar diferencias introducidas por Git en Windows. La relectura de F2 comprobó además todos los valores y ausencias.

Se mantuvieron las 8.579 personas, se recodificaron 883 códigos de no respuesta y no se realizaron imputaciones ni eliminaciones por faltantes o extremos. El archivo principal conserva 19 columnas originales, la diferencia de edad calculada y una columna reservada para años de convivencia, sin valores por falta de una referencia temporal validada.

La prueba integral se realizó con una instalación nueva en el equipo de desarrollo; no representa una prueba en otros sistemas operativos. La ejecución de F2 en el otro equipo también cuenta con un registro independiente publicado por Karla.

## Evidencias y repetición del procedimiento

- [Registro estructurado de esta prueba](Verificacion_reproduccion_completa.json).
- [Verificación de F2 por Karla](../../F2/docs/Verificacion_F2_Karla.md).
- [Instalación y ejecución](Instalacion_y_ejecucion.md).

Para repetir la prueba, clonar el repositorio, crear el entorno, instalar las dependencias, registrar el kernel y obtener los datos desde la raíz del repositorio con `python F1/src/convertir_enssex.py --download`. Después, ejecutar F1 y F2 desde kernels nuevos. Los CSV procesados y el diccionario se incluyen al clonar; la base original se obtiene mediante el script documentado.
