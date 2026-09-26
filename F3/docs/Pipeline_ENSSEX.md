# Flujo principal de F3

`PipelineENSSEX`, en `F3/src/pipeline_enssex.py`, coordina el preprocesamiento
en memoria. Recibe la base original cargada y el esquema de F2. Devuelve los
productos y su evidencia, sin descargar ni escribir archivos.

## Recorrido y responsabilidades

1. `seleccionar_convivientes`: filtra `p81 = 1` y `p83 = 1`, selecciona las
   19 columnas originales y registra los conteos.
2. `LimpiadorCodigos`: aplica las reglas de F2 y registra la recodificación.
3. Tres objetos `TratamientoFaltantes`, uno por variable central: aplican
   `conservar_faltantes`. No eliminan filas ni reemplazan ausencias.
4. `TipificadorCategorias`: declara las categorías nominales y ordinales.
5. `construir_derivadas`: calcula `p4 - p91`, conservando su signo y faltantes.
6. `codificar_nominales`: genera la matriz auxiliar con folio e indicadores.
7. `validar_resultado`: verifica integridad, categorías, ausencias, derivada
   y correspondencia de la matriz con la tabla principal.

La clase usa **composición**: reúne objetos con responsabilidades específicas.
Los transformadores heredan de `Transformador`. Un bucle llama a sus métodos
`ajustar()` y `transformar()` mediante la misma interfaz, ejecutando la operación
propia de cada clase hija: **polimorfismo**. El esquema se conserva como copia
interna; cada ejecución crea sus propios objetos y devuelve tablas independientes.
Este control de configuración y resultados aporta **encapsulamiento**.

La selección, la derivación y la codificación permanecen como funciones de F2.
El pipeline coordina las etapas sin duplicar sus reglas. No hereda de
`Transformador`: recibe una base y entrega varios productos y evidencias, en vez
de representar una transformación individual de una tabla.

Strategy ya está implementado en `TratamientoFaltantes`. El flujo principal fija
la estrategia de conservación. Las simulaciones de imputación siguen fuera de
este recorrido y no se convierten en respuestas categóricas ni productos finales.

## Ejecución

Desde la raíz del repositorio, con el entorno del proyecto, este ejemplo verifica
la identidad del CSV mediante la evidencia de conversión antes de procesarlo:

```python
from pathlib import Path
import json
import sys

raiz = Path.cwd()
sys.path.insert(0, str(raiz / 'F2/src'))
sys.path.insert(0, str(raiz / 'F3/src'))

from preparar_enssex import cargar_base
from pipeline_enssex import PipelineENSSEX

esquema = json.loads(
    (raiz / 'F2/docs/esquema_variables_F2.json').read_text(encoding='utf-8')
)
evidencia = json.loads(
    (raiz / 'docs/datos/verificacion_conversion_enssex.json').read_text(encoding='utf-8')
)
base = cargar_base(raiz / 'data/raw' / evidencia['csv_file'], evidencia, esquema)
resultados = PipelineENSSEX(esquema).ejecutar(base)
print(resultados['principal'].shape)
print(resultados['nominales'].shape)
```

El pipeline no comprueba la identidad de un archivo a partir de una tabla en
memoria: esa responsabilidad pertenece a `cargar_base`. Las pruebas pequeñas
pueden pasar una tabla controlada directamente.

| Clave del resultado | Contenido |
|---|---|
| `seleccion` | Selección original, con códigos anteriores a la limpieza. |
| `limpia` | Tabla limpia anterior a la tipificación. |
| `tipificada` | Tabla con categorías, antes de agregar la derivada. |
| `principal` | Tabla final: 19 columnas originales y diferencia de edad. |
| `nominales` | Matriz auxiliar de indicadores nominales. |
| `flujo_seleccion` | Conteos de base, pareja y convivencia. |
| `resumen_limpieza` | Recodificaciones y faltantes por variable. |
| `resumen_faltantes` | Conservación de las tres centrales, sin imputación. |
| `disponibilidad` | Denominadores específicos de cada comparación. |
| `validaciones` | Comprobaciones del resultado y estado de cada una. |

Con ENSSEX real se esperan 8.579 filas, 20 columnas principales, 65 columnas
nominales y 130 comprobaciones. Son resultados del conjunto verificado, no límites
impuestos a cualquier muestra de entrada. No se calcula duración de convivencia.

## Pruebas y alcance

```bash
python F3/tests/validar_transformadores.py
python F3/tests/validar_faltantes.py
python F3/tests/validar_pipeline.py
```

La prueba del pipeline cubre filtros conocidos, derivada negativa y ausente,
categorías, indicadores de ausencia, una sola persona, centrales sin respuesta,
copias independientes y recuperación tras errores. Rechaza entradas vacías,
columnas faltantes o duplicadas, índices repetidos, folios duplicados entre
seleccionados, códigos inválidos, fechas inválidas y ausencia de convivientes.

La comparación real reconstruye F2 mediante sus funciones y exige igualdad exacta
de productos e intermedios, incluidos índices, tipos, categorías y orden. También
comprueba que la base recibida permanezca intacta.

Conservar tablas intermedias y realizar copias facilita la revisión pero consume
memoria: no se afirma una mejora de rendimiento sin medirla. Siguen pendientes las
mediciones, la exportación propia de F3, el notebook y la reproducción desde un
entorno limpio. Esta integración acredita el recorrido en memoria, no la entrega
completa de Sumativa 2.
