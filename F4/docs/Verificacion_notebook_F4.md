# Verificación del notebook integrador de F4

El 2 de octubre de 2026 ejecutamos de principio a fin
`F4/notebooks/F4_Integrador_ENSSEX.ipynb` en el equipo de Guillermo, desde un kernel
nuevo `grupo9_mcdi500`, sobre el merge `3e6d5d6` del PR #14. El trabajo permanece
en la rama `tarea/s3-notebook-integrador`, pendiente de revisión y publicación.

## Ejecución completa

El notebook conserva 29 celdas, con las 14 celdas de código ejecutadas en orden,
contadores consecutivos, cero errores y ninguna salida `stderr` en las celdas.
Incluye las tres figuras generadas en esta ejecución. No se omitieron pruebas,
importaciones ni mediciones.

Inicio UTC: `2026-10-02T22:17:05.656186+00:00`.
Fin UTC: `2026-10-02T22:18:23.861917+00:00`.

| Comprobación | Resultado |
|---|---|
| Entorno | Python 3.13.15, Windows; dependencias compatibles |
| Carga de pyreadstat | Versión 1.3.6, importación correcta |
| Fuente y huellas exactas SAV/CSV | 20.392 × 1.126; coincidencia |
| Casos controlados F2 | 21 correctos |
| Scripts F3–F4 | Nueve, todos con código de salida 0 |
| Equivalencia F2/F3 | Valores, tipos, categorías, orden y ausencias iguales |
| Validación del producto | 130 comprobaciones correctas |
| Principal / nominal / interpretable | 8.579 × 20 / 8.579 × 65 / 8.579 × 34 |
| Códigos de no respuesta recodificados | 883; sin imputación ni descarte global |
| Exportación F3 y F4 | Relectura exacta; CSV y manifiestos juntos |
| Ocho tablas y resumen analítico | Coinciden con la referencia del PR #14 |
| Figuras | Tres PNG embebidos y tres SVG exportados |
| Diferencia de edad | Cinco tamaños, cinco repeticiones; igualdad antes de medir |
| Lectura SAV completa y selectiva | Equivalencia de datos y metadatos; cinco repeticiones |
| Integridad | Originales, módulos y productos previos intactos |

La dependencia económica de la pareja (`p93`) conserva 8.502 respuestas válidas y
77 ausentes. La valoración de la vida sexual (`i_6_p9`) usa una base de comparación
de 8.399 personas; el bienestar mental o emocional percibido (`i_2_p9`), de 8.491.
Sexo asignado al nacer (`p1`) registra 2.822 hombres y 5.757 mujeres, sin ausencias.

Los siete scripts de F3 comprueban transformadores, faltantes, pipeline, exportación,
medición de lectura SAV, diferencia de edad y medición de algoritmos. Los dos de F4
comprueban datos interpretables y análisis descriptivo. El notebook guarda sus
registros; `ejecucion_integrador.json`, dentro del destino local de cada ejecución,
conserva versiones, huellas y mediciones completas. Los tiempos pueden variar entre
equipos y no son una condición de igualdad analítica.

## Incidencia del entorno y nueva ejecución

El primer intento se detuvo por un bloqueo de Smart App Control de Windows sobre
`_readstat_parser.cp313-win_amd64.pyd`. Se diagnosticó mediante eventos de integridad
de código. Una copia separada permitió verificar parcialmente el resto del flujo,
sin modificar el notebook de entrega ni declarar completa esa ejecución.

Después del cambio de configuración informado por Guillermo, se comprobó la carga
de pyreadstat y se ejecutó el notebook completo desde un kernel nuevo. Esta ejecución
incluye la prueba y medición SAV previamente pendientes. El cambio de configuración
describe lo ocurrido en este equipo; no es un requisito del proyecto ni una instrucción
para otros equipos.

El lanzador de Jupyter emitió avisos sobre la adaptación del bucle de eventos de
Windows y el transporte TCP del kernel local. No interrumpieron la ejecución ni
produjeron errores en las celdas. Las comprobaciones se basan en los resultados y
contadores guardados, no en la ausencia de mensajes del lanzador.

## Reproducción y estado de revisión

Las [instrucciones de F4](../README.md) describen las entradas y la ejecución desde
Git Bash y JupyterLab. Cada ejecución completa crea una carpeta nueva bajo
`F4/resultados_locales`; los CSV se conservan junto con sus JSON y los originales
y resultados publicados permanecen intactos. No se cambiaron módulos ni las tablas
aprobadas para completar esta prueba.

La revisión cruzada de este notebook por Karla sigue pendiente. Su ejecución y
aprobación del PR #14 corresponden a los módulos, tablas y figuras anteriores.
El informe, la presentación audiovisual y la revisión integral de la entrega siguen
pendientes. Esta verificación no acredita el envío de la evaluación.
