# Fase 2 · Limpieza y transformación de ENSSEX

La preparación utiliza la selección acordada de 19 columnas originales y conserva por separado los dos resultados de bienestar. El alcance es descriptivo y comparativo de la muestra, sin ponderación ni interpretación causal.

## Ejecución

1. Preparar el entorno siguiendo la [guía de instalación](../F1/docs/Instalacion_y_ejecucion.md).
2. Disponer del CSV original según la [guía de obtención](../docs/datos/Obtencion_y_conversion_ENSSEX.md).
3. Abrir [F2_limpieza_transformacion_ENSSEX.ipynb](notebooks/F2_limpieza_transformacion_ENSSEX.ipynb) desde JupyterLab.
4. Seleccionar **Python (grupo9-mcdi500)** y usar **Kernel → Restart Kernel and Run All Cells**.
5. Revisar las tablas de evidencia y el cierre, que debe indicar OK en sus siete comprobaciones.

El notebook explica por qué se conserva cada una de las 19 columnas, junto con su nombre y pregunta asociada. Las tablas y gráficos muestran nombres comprensibles y códigos para facilitar su lectura.

El notebook se ejecuta desde F2/notebooks. No necesita variables de una sesión de F1. La semilla declarada es 42; el flujo es determinista y no realiza muestreo. Cada ejecución regenera los CSV y la documentación de resultados.

## Productos y resultados

- 8,579 personas con p81=1 y p83=1.
- 883 celdas NS/NR recodificadas; 0 imputaciones y 0 filas eliminadas por faltantes o extremos.
- Conjunto principal: 20 columnas; las 19 originales preparadas y la diferencia de edad calculada.
- Matriz nominal auxiliar: 65 columnas, incluido el folio.
- 130 invariantes, 21 casos controlados y relectura completa de ambos CSV verificados.

Los CSV `enssex_convivientes_F2.csv` y `enssex_convivientes_F2_nominales.csv` se generan en `F2/data/processed`, se incluyen en el repositorio para facilitar su revisión y pueden reconstruirse ejecutando este notebook. La entrada compartida está en `data/raw`; los módulos propios y las pruebas de F2 están en `F2/src` y `F2/tests`.

## Documentación y código

- [Bitácora de decisiones y alternativas](docs/Bitacora_decisiones_F1_F2.md).
- [Resultados para integrar en el informe](docs/Resultados_preparacion_F2.md).
- [Diccionario del conjunto procesado](docs/Diccionario_procesado_F2.md).
- [Selección y justificación de las 19 columnas](docs/Seleccion_y_justificacion_variables_F2.md).
- [Configuración de variables](docs/esquema_variables_F2.json).
- [Evidencia de validación](docs/validacion_F2.json).
- [Funciones de preparación](../F2/src/preparar_enssex.py).
- [Casos controlados de validación](tests/validar_preparacion_enssex.py).
- [Gráficos](src/visualizar_enssex.py), [presentación de tablas](src/presentacion_enssex.py) y [generación de documentación](src/documentar_enssex.py).

## Límites

La duración de convivencia no se calcula: las fuentes consultadas no definen el evento que representa `fecha`. La columna vacía anios_convivencia_aprox no se genera ni se exporta. Se conservan los extremos estadísticos con su diagnóstico; no se declaran errores sin respaldo.
