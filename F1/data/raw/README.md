# Datos originales y copia de lectura

El proyecto conserva el SAV original de ENSSEX 2022–2023 y una copia CSV de su contenido completo. La [guía de obtención y conversión](../../docs/Obtencion_y_conversion_ENSSEX.md) documenta la fuente oficial, la licencia CC0, la versión utilizada y las comprobaciones de integridad.

## Archivos de entrada

- `20241205_enssex_data.sav`: original descargado, que se conserva sin modificar.
- `20241205_enssex_desde_sav.csv`: copia generada desde el SAV, con separador `;`, codificación `utf-8-sig`, punto decimal y sin columna de índice.
- `etiquetas_y_metadatos_ENSSEX.json`: etiquetas, categorías, formatos y metadatos que complementan el CSV.

Desde la raíz del repositorio, con el entorno virtual activo y las dependencias instaladas:

```bash
python F1/src/convertir_enssex.py --download
```

El script descarga el SAV si no está disponible, verifica su huella y genera y comprueba el CSV. Si el SAV ya existe, lo verifica y reutiliza. Para trabajar sin conexión con el original ya descargado, se omite `--download`. La evidencia queda en [verificacion_conversion_enssex.json](../../docs/verificacion_conversion_enssex.json).

El notebook preliminar utiliza `20241205_enssex_desde_sav.csv`. En la copia local del equipo también se conserva el CSV descargado `20241205_enssex_data.csv`; ese archivo no es la entrada utilizada ni se genera con el procedimiento de conversión documentado.

Los datos se mantienen fuera de Git mediante `.gitignore`; este README, el script, las instrucciones y la evidencia sí forman parte de la documentación compartida. La conversión no filtra ni limpia los registros. Las salidas de la preparación analítica se guardarán en `F1/data/processed`.
