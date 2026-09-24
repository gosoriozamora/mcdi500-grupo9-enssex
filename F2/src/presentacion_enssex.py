"""Etiquetas legibles y presentación de tablas sin alterar los datos de trabajo."""
import re
import numpy as np
import pandas as pd


def etiqueta_variable(nombre, esquema):
    """Nombre comprensible y código técnico, sin renombrar columnas del dataset."""
    nombres = {v['nombre']: v['nombre_legible'] for v in esquema['variables']}
    nombres.update({'diferencia_edad_pareja': 'Diferencia de edad con la pareja',
                    'anios_convivencia_aprox': 'Años aproximados de convivencia'})
    return f'{nombres[nombre]} ({nombre})' if nombre in nombres else nombre



def rotular_referencias(texto, esquema):
    """Explica códigos aislados dentro de una salida destinada a lectura humana."""
    nombres = [v['nombre'] for v in esquema['variables']] + ['diferencia_edad_pareja', 'anios_convivencia_aprox']
    patron = r'(?<![\w])(' + '|'.join(re.escape(n) for n in sorted(nombres, key=len, reverse=True)) + r')(?![\w])'
    return re.sub(patron, lambda m: etiqueta_variable(m.group(0), esquema), str(texto))



def presentar_tabla(tabla, esquema):
    """Prepara solo la vista: nombres de preguntas y etiquetas; no altera los datos."""
    vista = tabla.copy(deep=True)
    por_nombre = {v['nombre']: v for v in esquema['variables']}
    for columna in vista:
        if columna == 'variable':
            vista[columna] = vista[columna].map(lambda v: etiqueta_variable(v, esquema))
        elif columna in por_nombre and por_nombre[columna]['categorias']:
            etiquetas = por_nombre[columna]['etiquetas']
            vista[columna] = vista[columna].map(
                lambda v: 'Sin respuesta' if pd.isna(v) else f'{etiquetas.get(str(int(v)), str(v))} ({int(v)})')
        elif vista[columna].dtype == 'object' or pd.api.types.is_string_dtype(vista[columna].dtype):
            # Las preguntas y motivos originales ya se presentan junto a un nombre
            # completo. No se altera su redacción al preparar las tablas de selección.
            if columna not in ['Pregunta o nombre del dato', 'Por qué la conservamos']:
                vista[columna] = vista[columna].map(
                    lambda v: rotular_referencias(v, esquema) if isinstance(v, str) else v)
    vista = vista.rename(columns={n: etiqueta_variable(n, esquema) for n in por_nombre if n in vista.columns})
    vista = vista.rename(columns={
        'variable': 'Variable (nombre y código)', 'rol': 'Función',
        'tipo_lectura': 'Tipo al leer el archivo', 'tipo_analitico': 'Tipo analítico',
        'distintos': 'Valores distintos', 'vacios': 'Campos vacíos', 'no_respuesta': 'Respuestas especiales',
        'codigos_observados': 'Códigos observados', 'no_respuesta_documentada': 'Códigos de no respuesta',
        'vacios_originales': 'Vacíos originales', 'NS_NR_a_faltante': 'NS/NR convertidos en ausencias',
        'faltantes_despues': 'Faltantes después', 'filas_eliminadas': 'Filas eliminadas',
        'vida_sexual_valida': 'Valoraciones válidas de vida sexual',
        'bienestar_emocional_valido': 'Valoraciones válidas de bienestar emocional',
        'porcentaje_faltante': 'Porcentaje de faltantes',
        'categorias_documentadas': 'Categorías documentadas',
        'indicadores_incluida_ausencia': 'Indicadores, incluida ausencia',
        'varianza_codigos': 'Varianza de códigos', 'cambio_varianza_pct': 'Cambio de varianza (%)',
        'valores_fraccionarios': 'Valores fraccionarios', 'senalados_IQR': 'Casos señalados por IQR',
        'limite_inferior': 'Límite inferior IQR', 'limite_superior': 'Límite superior IQR',
    })
    return vista
