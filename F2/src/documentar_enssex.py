"""Generación de bitácora, diccionario, README y resultados de F2."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from presentacion_enssex import etiqueta_variable, presentar_tabla


def tabla_markdown(tabla):
    """Evita una dependencia extra para producir documentación con las cifras reales."""
    def texto(valor):
        if pd.isna(valor):
            return '—'
        if isinstance(valor, (float, np.floating)):
            return f'{valor:.3f}'
        return str(valor).replace('|', '/').replace('\n', ' ')
    lineas = ['| '+' | '.join(map(str,tabla.columns))+' |', '| '+' | '.join(['---']*len(tabla.columns))+' |']
    lineas.extend('| '+' | '.join(texto(v) for v in fila)+' |' for fila in tabla.itertuples(index=False, name=None))
    return '\n'.join(lineas)



def bitacora_decisiones(base, seleccion, limpia, final, matriz, impacto, disponibilidad, atipicos, tiempo):
    """Una fila por decisión con motivo, alternativa descartada y efecto medido."""
    faltantes = int(impacto['NS_NR_a_faltante'].sum())
    completos = int(disponibilidad.loc[disponibilidad['criterio'].eq('Todas las 19 originales completas'), 'disponibles'].iloc[0])
    filas = [
        ('F1-01','F1','Conservar el original y su huella','Mantener trazabilidad de la conversión SAV–CSV','Editar raw en cada fase',f'{len(base)} filas y {len(base.columns)} columnas originales intactas'),
        ('F1-02','F1','Usar 19 columnas: 3 centrales, 12 complementarias y 4 auxiliares','Responder la pregunta y contextualizarla con el alcance acordado','Seleccionar todas las columnas o mezclar los dos resultados','19 seleccionadas; 2 resultados ordinales separados; sin ponderadores ni inferencia poblacional'),
        ('F2-01','F2','Seleccionar p81=1 y p83=1 conjuntamente','La unidad de estudio es la persona que convive con su pareja','Usar solo estado civil o uno de los filtros',f'{len(base)} → {len(seleccion)} personas; {len(base)-len(seleccion)} fuera del alcance'),
        ('F2-02','F2','Comprobar folios antes de limpiar','Una repetición requiere investigación; no elegir arbitrariamente una respuesta','drop_duplicates automático',f'{int(seleccion.folio_encuesta.isna().sum())} folios ausentes; {int(seleccion.folio_encuesta.duplicated().sum())} repetidos; 0 filas eliminadas'),
        ('F2-03','F2','Convertir NS/NR según cada pregunta','Los códigos especiales no son respuestas sustantivas y contaminan los cálculos','Reemplazar 8, 9 o 99 globalmente',f'{faltantes} celdas recodificadas; 0 cambios en regiones válidas, estado civil 8 e ingreso relativo 6'),
        ('F2-04','F2','Conservar faltantes y usar denominadores por comparación','Evitar atribuir una respuesta íntima no observada; la sensibilidad muestra efectos de imputar','Eliminar toda fila incompleta o imputar media/mediana',f'0 valores imputados; 0 personas eliminadas por faltantes; casos completos globales conservarían {completos} de {len(seleccion)}'),
        ('F2-05','F2','Conservar extremos y registrar señales de revisión','La regla IQR detecta rareza, no demuestra error; no hay fuente para corregir las edades','Eliminar o winsorizar por IQR',f'{int(atipicos.senalados_IQR.sum())} señales variable-persona en {len(atipicos)} variables, no personas únicas; 0 recortes'),
        ('F2-06','F2','Tipificar ordinales con orden explícito y nominales sin orden','El tipo de almacenamiento no define la escala de medición','Orden alfabético o tratar códigos nominales como cantidades','5 ordinales con orden de códigos declarado; p93 aumenta hacia menor dependencia; nominales conservan significado'),
        ('F2-07','F2','Calcular p4 menos p91','Diferencia interpretable en años, conservando el signo','Restar códigos de no respuesta o usar valor absoluto',f'{int(final.diferencia_edad_pareja.notna().sum())} diferencias calculadas; rango {final.diferencia_edad_pareja.min()} a {final.diferencia_edad_pareja.max()} años'),
        ('F2-08','F2','Dejar duración de convivencia sin calcular','fecha tiene formato válido, pero su evento de referencia no está documentado','Asumir fecha de entrevista, usar año actual o 2022 para todas las personas','anios_convivencia_aprox no se genera ni se exporta; se retira la columna vacía observada en S1'),
        ('F2-09','F2','Exportar one-hot en una matriz auxiliar','Dar una representación numérica a las nominales sin inventar distancias','Reemplazar el dataset interpretable por dummies o usar folio como predictor',f'{len(matriz)} filas; {len(matriz.columns)-1} indicadores más folio; 1 indicador explícito de ausencia por variable'),
        ('F2-10','F2','Mantener edades y diferencia en años; no escalar','El alcance actual es descriptivo; no hay algoritmo basado en distancias que necesite escalamiento','Normalizar automáticamente todas las columnas','0 columnas escaladas; códigos ordinales no tratados como mediciones continuas'),
        ('F2-11','F2','Exportar CSV con esquema y comprobar su relectura','CSV no conserva categorías de pandas; el diccionario declara tipos, orden y ausencias','Entregar solo un CSV sin significado de los códigos',f'{len(final)} filas × {len(final.columns)} columnas; 19 originales preparadas + diferencia calculada'),
    ]
    return pd.DataFrame(filas,columns=['id','fase','decision','motivo','alternativa_descartada','impacto'])



def documentar_resultados(carpeta, esquema, resumen, tablas, bitacora, final):
    """Genera las cifras para el informe desde los mismos resultados del notebook."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta/'validacion_F2.json').write_text(json.dumps(resumen,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    contenido = '# Bitácora de decisiones de F1 y F2\n\n'
    contenido += 'Los antecedentes de F1 se contrastan con su notebook y con la evidencia de conversión. Los impactos de F2 se calculan en cada ejecución. Las dos valoraciones se mantienen separadas; el alcance es descriptivo y comparativo de la muestra, sin ponderación.\n\n'
    contenido += tabla_markdown(presentar_tabla(bitacora, esquema))+'\n\n'
    contenido += 'Las imputaciones se evaluaron solo como escenarios de sensibilidad; ninguna se aplicó. La duración de convivencia queda sin calcular hasta documentar una referencia temporal válida.\n'
    (carpeta/'Bitacora_decisiones_F1_F2.md').write_text(contenido,encoding='utf-8')
    texto = '# Resultados de la preparación de ENSSEX\n\n'+esquema['pregunta']+'\n\n'
    texto += (f"Se conservan {len(final):,} personas seleccionadas con p81=1 y p83=1. El conjunto principal tiene {len(final.columns)} columnas: las 19 originales preparadas y la diferencia de edad calculada. La duración de convivencia no se calcula ni se exporta por falta de una referencia temporal documentada. Se retira la columna vacía de la versión anterior, atendiendo la observación de S1.\n\n")
    texto += 'No se imputan respuestas ni se eliminan personas por no respuesta o por extremos estadísticos. Los códigos originales y sus motivos de ausencia se pueden recuperar en raw mediante folio_encuesta. Cada análisis posterior debe indicar sus propios casos válidos y no interpretar estas cifras como estimaciones poblacionales.\n\n'
    for titulo, tabla in tablas.items():
        texto += '## '+titulo+'\n\n'+tabla_markdown(presentar_tabla(tabla, esquema))+'\n\n'
    texto += '## Límites y continuidad\n\nLa varianza de códigos en los escenarios de imputación es un diagnóstico mecánico de sensibilidad; no demuestra que las escalas ordinales tengan intervalos iguales. Las señales temporales calculadas bajo la hipótesis de que fecha fuera la referencia tampoco confirman errores por sí solas. Los casos extremos permanecen para revisión y análisis de sensibilidad en F3.\n\n'
    texto += '## Ubicación de los productos\n\nLos CSV se generan en F2/data/processed. La configuración y el diccionario están en F2/docs/esquema_variables_F2.json y Diccionario_procesado_F2.md. La bitácora y validacion_F2.json permiten contrastar estas cifras con las salidas del notebook.\n'
    (carpeta/'Resultados_preparacion_F2.md').write_text(texto,encoding='utf-8')
    filas=[]
    for v in esquema['variables']:
        filas.append({'variable':etiqueta_variable(v['nombre'], esquema),'rol':v['rol'],'tipo_en_memoria':str(final[v['nombre']].dtype),
                      'descripcion':v['descripcion'],'codigos_validos':'; '.join(f'{k}={val}' for k,val in v['etiquetas'].items()) or v['tipo'],
                      'NS_NR_en_raw':str(v['no_respuesta']),'orden':str(v['categorias']) if v['ordenada'] else 'Sin orden nominal / no aplica',
                      'faltantes':int(final[v['nombre']].isna().sum())})
    for nombre in esquema['derivadas']:
        filas.append({'variable':etiqueta_variable(nombre, esquema),'rol':'derivada','tipo_en_memoria':'Int64','descripcion':esquema['derivadas'][nombre],
                      'codigos_validos':'Enteros con signo' if nombre.startswith('diferencia') else 'Sin calcular',
                      'NS_NR_en_raw':'No aplica','orden':'No aplica','faltantes':int(final[nombre].isna().sum())})
    dic = '# Diccionario del conjunto procesado de F2\n\n'
    dic += '19 columnas originales preparadas y una derivada calculada: diferencia de edad. La duración de convivencia no se exporta por falta de una referencia temporal validada. CSV: separador punto y coma, UTF-8 con BOM, sin índice, fecha ISO AAAA-MM-DD, códigos enteros y campos vacíos para ausencias. El folio se lee como texto. Para reconstruir categorías y su orden se utiliza esquema_variables_F2.json.\n\n'
    dic += tabla_markdown(pd.DataFrame(filas))+'\n\n'
    dic += 'La matriz auxiliar nominal contiene folio_encuesta y columnas nombre__codigo, más nombre__sin_respuesta para cada nominal. Cada bloque suma uno por persona. Los indicadores no aumentan la selección sustantiva de 19 variables y no forman parte del CSV principal de 20 columnas.\n'
    (carpeta/'Diccionario_procesado_F2.md').write_text(dic,encoding='utf-8')
    (carpeta/'Seleccion_y_justificacion_variables_F2.md').write_text('# Selección de variables de ENSSEX\n\n'+documentar_seleccion(esquema),encoding='utf-8')
    readme = '''# Fase 2 · Limpieza y transformación de ENSSEX

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

'''
    readme += f"- {len(final):,} personas con p81=1 y p83=1.\n- {resumen['limpieza']['NS_NR_recodificados']} celdas NS/NR recodificadas; 0 imputaciones y 0 filas eliminadas por faltantes o extremos.\n"
    readme += f"- Conjunto principal: {len(final.columns)} columnas; las 19 originales preparadas y la diferencia de edad calculada.\n"
    readme += f"- Matriz nominal auxiliar: {resumen['exportados']['nominales']['columnas']} columnas, incluido el folio.\n"
    readme += f"- {resumen['validaciones']['invariantes']} invariantes, {resumen['validaciones']['casos_controlados']} casos controlados y relectura completa de ambos CSV verificados.\n\n"
    readme += '''Los CSV `enssex_convivientes_F2.csv` y `enssex_convivientes_F2_nominales.csv` se generan en `F2/data/processed`, se incluyen en el repositorio para facilitar su revisión y pueden reconstruirse ejecutando este notebook. La entrada compartida está en `data/raw`; los módulos propios y las pruebas de F2 están en `F2/src` y `F2/tests`.

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
'''
    (carpeta.parent/'README.md').write_text(readme,encoding='utf-8')



def documentar_seleccion(esquema):
    """Justificación legible por columna, compartida por notebook y documentación."""
    texto = '''## Por qué seleccionamos estas 19 columnas

La pregunta necesita identificar a las personas que conviven con su pareja y comparar dos valoraciones de bienestar entre los niveles de dependencia económica. Ese es el núcleo del estudio. Conservamos además datos que permiten describir a esas personas, contextualizar futuras comparaciones y comprobar la calidad de los registros.

La selección se organiza por su utilidad concreta:

- **3 centrales:** una define los grupos de dependencia económica y dos registran las valoraciones que se compararán por separado.
- **12 complementarias:** describen el contexto sociodemográfico, de la relación y de salud. Su conservación permite evaluar análisis posteriores sin volver a seleccionar datos del archivo completo.
- **4 auxiliares:** dos definen quién pertenece a la población, una identifica cada registro y una permite revisar una posible referencia temporal.

**No todas las 19 columnas son necesarias en cada comparación.** Para delimitar la población y abordar la pregunta básica utilizamos las tres centrales y los dos filtros de pareja y convivencia. Las demás cumplen una función de contexto o de control técnico. No se eligieron porque ya hayan demostrado una asociación con el bienestar ni porque deban entrar juntas en un modelo. Cada uso posterior dependerá de su pertinencia y de la calidad de las respuestas.

Las tablas indican la pregunta asociada, con ajustes menores de redacción ya documentados en F1. Región, identificador y fecha son campos de la base; no se presentan como preguntas numeradas al encuestado. El código se mantiene entre paréntesis para poder localizar cada columna en el archivo.

'''
    grupos = [('Centrales: qué comparamos y entre qué grupos', 'central'),
              ('Complementarias: características sociodemográficas', 'sociodemografica'),
              ('Complementarias: relación de pareja y salud', 'relacion_salud'),
              ('Auxiliares: población y trazabilidad', 'auxiliar')]
    for titulo, grupo in grupos:
        filas = [{'Variable y código': etiqueta_variable(v['nombre'], esquema),
                  'Pregunta o nombre del dato': v['descripcion'],
                  'Por qué la conservamos': v['justificacion']}
                 for v in esquema['variables'] if v['grupo_explicativo'] == grupo]
        texto += '### ' + titulo + '\n\n' + tabla_markdown(pd.DataFrame(filas)) + '\n\n'
    texto += '''### Qué aporta esta selección a las siguientes fases

En F2 comprobamos la disponibilidad y calidad de estas columnas. En F3 podremos comparar cada valoración entre los grupos de dependencia, describir la composición de esos grupos y evaluar análisis por características personales o de la relación, siempre que existan suficientes respuestas válidas. Conservar una columna no la convierte automáticamente en una causa, un predictor o una variable de ajuste obligatoria.

La edad de la persona encuestada (p4) y la edad de su pareja (p91) permiten calcular la diferencia de edad. El año de inicio de convivencia (p84) y la fecha registrada (fecha) permitirían calcular una duración aproximada solo si se confirma una referencia temporal válida. Por eso conservamos esos datos, pero los años de convivencia permanecen sin calcular. Solo la diferencia de edad se exporta como derivada, aparte de las 19 columnas originales.

'''
    return texto
