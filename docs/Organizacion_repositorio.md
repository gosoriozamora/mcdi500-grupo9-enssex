# Organización del repositorio

Los archivos se organizan por fase y responsabilidad. Los originales compartidos y su conversión están en la raíz; los componentes propios de F2 permanecen dentro de esa fase.

| Responsabilidad | Ubicación |
|---|---|
| Fuente original y copia de lectura | `data/raw` |
| Obtención y conversión de SAV a CSV | `src/convertir_enssex.py` |
| Guía y registro de conversión | `docs/datos` |
| Definición y reconocimiento inicial | `F1/notebooks` |
| Validación preliminar histórica | `F1/antecedentes` |
| Preparación, transformación, validación y exportación | `F2/src/preparar_enssex.py` |
| Gráficos | `F2/src/visualizar_enssex.py` |
| Etiquetas y presentación de tablas | `F2/src/presentacion_enssex.py` |
| Generación de documentación | `F2/src/documentar_enssex.py` |
| Casos controlados | `F2/tests/validar_preparacion_enssex.py` |
| Productos procesados | `F2/data/processed` |
| Flujo reproducible | `F2/notebooks/F2_limpieza_transformacion_ENSSEX.ipynb` |

El notebook conecta las responsabilidades. La preparación no importa los módulos de gráficos ni de documentación. Los módulos de presentación y documentación no modifican las reglas de limpieza.

Esta reorganización conserva las reglas analíticas y las columnas de la entrega anterior. Los informes PDF, el mapa entregado y las evidencias previas conservan su carácter histórico: sus rutas describen la estructura existente cuando se elaboraron. Para ejecutar la versión actual deben usarse el README y las guías actualizadas. La retirada de la derivada vacía y el desarrollo de POO corresponden a cambios posteriores.
