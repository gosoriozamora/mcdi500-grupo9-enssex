# Verificación de la reorganización

Fecha: 24 de septiembre de 2026.

Comprobamos la reorganización mediante la ejecución completa de F1 y F2 con kernels nuevos e independientes, utilizando el entorno virtual existente. No se reinstalaron las dependencias.

- F1: 10 celdas de código ejecutadas sin errores.
- F2: 13 celdas de código ejecutadas sin errores, 130 invariantes y 21 casos controlados superados.
- Originales y dos productos CSV: identidad byte a byte frente al estado anterior, mediante SHA-256.
- Funciones de preparación, gráficos y presentación: cuerpos equivalentes mediante comparación de sus árboles sintácticos. Las funciones de documentación actualizan las rutas publicadas.
- Casos controlados: archivo conservado sin cambios; cambió su ubicación.
- Enlaces locales de la documentación vigente: comprobados. Se excluyen antecedentes, checkpoints y documentos históricos, cuyas rutas corresponden a la entrega original.
- Interfaz de conversión: comprobada mediante `python src/convertir_enssex.py --help`. No fue necesaria una nueva descarga ni conversión.

La ejecución conserva 8.579 personas, 21 columnas en el producto principal y 65 en la matriz nominal. La eliminación de la derivada vacía se abordará por separado.

El detalle y las huellas previas están en [Verificacion_reorganizacion.json](Verificacion_reorganizacion.json). Los notebooks conservan las salidas de esta ejecución; [validacion_F2.json](../F2/docs/validacion_F2.json) registra las comprobaciones y las huellas de los módulos actuales.

La prueba no sustituye la reproducción posterior desde una instalación nueva ni la revisión del otro integrante.
