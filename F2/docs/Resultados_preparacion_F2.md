# Resultados de la preparación de ENSSEX

¿Cómo varían la valoración de la vida sexual y el bienestar mental o emocional percibido según el grado de dependencia económica de la pareja entre las personas encuestadas en ENSSEX 2022–2023 que conviven con ella?

Se conservan 8,579 personas seleccionadas con p81=1 y p83=1. El conjunto principal tiene 21 columnas: las 19 originales preparadas, la diferencia de edad calculada y el espacio reservado para los años de convivencia. Este último permanece sin valores por falta de una referencia temporal documentada. No debe incluirse en el cálculo de completitud de respuestas originales.

No se imputan respuestas ni se eliminan personas por no respuesta o por extremos estadísticos. Los códigos originales y sus motivos de ausencia se pueden recuperar en raw mediante folio_encuesta. Cada análisis posterior debe indicar sus propios casos válidos y no interpretar estas cifras como estimaciones poblacionales.

## Selección de la población

| etapa | filas | excluidas_en_paso |
| --- | --- | --- |
| Base completa | 20392 | 0 |
| Tiene pareja (Tiene pareja actualmente (p81)=1) | 11239 | 9153 |
| Además convive (Convive actualmente con su pareja (p83)=1) | 8579 | 2660 |

## Limpieza por columna

| Variable (nombre y código) | Vacíos originales | NS/NR convertidos en ausencias | Faltantes después | Filas eliminadas |
| --- | --- | --- | --- | --- |
| Dependencia económica de la pareja (p93) | 0 | 77 | 77 | 0 |
| Valoración de la vida sexual (i_6_p9) | 0 | 105 | 105 | 0 |
| Bienestar mental o emocional percibido (i_2_p9) | 0 | 11 | 11 | 0 |
| Edad de la persona encuestada (p4) | 0 | 0 | 0 | 0 |
| Sexo asignado al nacer (p1) | 0 | 0 | 0 | 0 |
| Género declarado (p3) | 0 | 3 | 3 | 0 |
| Nivel educacional (p5) | 0 | 0 | 0 | 0 |
| Región (region) | 0 | 0 | 0 | 0 |
| Estado conyugal o civil (p7) | 0 | 5 | 5 | 0 |
| Ingreso relativo respecto de la pareja (p92) | 0 | 170 | 170 | 0 |
| Año de inicio de convivencia (p84) | 0 | 0 | 0 | 0 |
| Edad de la pareja (p91) | 0 | 0 | 0 | 0 |
| Actividad sexual con la pareja en el último mes (p96) | 0 | 445 | 445 | 0 |
| Salud general percibida (p10) | 0 | 50 | 50 | 0 |
| Calidad de vida percibida (p8) | 0 | 17 | 17 | 0 |
| Tiene pareja actualmente (p81) | 0 | 0 | 0 | 0 |
| Convive actualmente con su pareja (p83) | 0 | 0 | 0 | 0 |
| Identificador de la encuesta (folio_encuesta) | 0 | 0 | 0 | 0 |
| Fecha registrada en la base (fecha) | 0 | 0 | 0 | 0 |

## Disponibilidad por análisis

| criterio | disponibles | no_disponibles |
| --- | --- | --- |
| Convivientes conservados | 8579 | 0 |
| Dependencia y valoración de vida sexual | 8399 | 180 |
| Dependencia y bienestar emocional | 8491 | 88 |
| Tres centrales completas | 8392 | 187 |
| Todas las 19 originales completas | 7825 | 754 |

## Disponibilidad por dependencia

| Dependencia económica de la pareja (p93) | personas | Valoraciones válidas de vida sexual | Valoraciones válidas de bienestar emocional |
| --- | --- | --- | --- |
| Sí, completamente (1) | 2197 | 2170 | 2194 |
| Sí, en parte (2) | 1987 | 1960 | 1986 |
| No (3) | 4318 | 4269 | 4311 |
| Sin respuesta | 77 | 75 | 77 |

## Alternativas de imputación evaluadas y descartadas

| Variable (nombre y código) | alternativa | filas | faltantes | imputados | Valores fraccionarios | Varianza de códigos | Cambio de varianza (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Dependencia económica de la pareja (p93) | Conservar faltantes | 8579 | 77 | 0 | 0 | 0.704 | 0.000 |
| Dependencia económica de la pareja (p93) | Eliminar solo para este cálculo | 8502 | 0 | 0 | 0 | 0.704 | 0.000 |
| Dependencia económica de la pareja (p93) | Imputar media global | 8579 | 0 | 77 | 77 | 0.698 | -0.898 |
| Dependencia económica de la pareja (p93) | Imputar mediana global | 8579 | 0 | 77 | 0 | 0.703 | -0.186 |
| Valoración de la vida sexual (i_6_p9) | Conservar faltantes | 8579 | 105 | 0 | 0 | 2.422 | 0.000 |
| Valoración de la vida sexual (i_6_p9) | Eliminar solo para este cálculo | 8474 | 0 | 0 | 0 | 2.422 | 0.000 |
| Valoración de la vida sexual (i_6_p9) | Imputar media global | 8579 | 0 | 105 | 105 | 2.392 | -1.224 |
| Valoración de la vida sexual (i_6_p9) | Imputar mediana global | 8579 | 0 | 105 | 0 | 2.394 | -1.158 |
| Valoración de la vida sexual (i_6_p9) | Imputar mediana por dependencia | 8579 | 2 | 103 | 0 | 2.395 | -1.136 |
| Bienestar mental o emocional percibido (i_2_p9) | Conservar faltantes | 8579 | 11 | 0 | 0 | 1.600 | 0.000 |
| Bienestar mental o emocional percibido (i_2_p9) | Eliminar solo para este cálculo | 8568 | 0 | 0 | 0 | 1.600 | 0.000 |
| Bienestar mental o emocional percibido (i_2_p9) | Imputar media global | 8579 | 0 | 11 | 11 | 1.598 | -0.128 |
| Bienestar mental o emocional percibido (i_2_p9) | Imputar mediana global | 8579 | 0 | 11 | 0 | 1.598 | -0.119 |
| Bienestar mental o emocional percibido (i_2_p9) | Imputar mediana por dependencia | 8579 | 0 | 11 | 0 | 1.598 | -0.119 |

## Revisión de valores extremos

| Variable (nombre y código) | n | min | Q1 | mediana | Q3 | max | Límite inferior IQR | Límite superior IQR | Casos señalados por IQR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Edad de la persona encuestada (p4) | 8579 | 18.000 | 34.000 | 47.000 | 60.000 | 100.000 | -5.000 | 99.000 | 1 |
| Edad de la pareja (p91) | 8579 | 18.000 | 35.000 | 48.000 | 61.000 | 100.000 | -4.000 | 100.000 | 0 |
| Año de inicio de convivencia (p84) | 8579 | 1942.000 | 1990.000 | 2005.000 | 2016.000 | 2022.000 | 1951.000 | 2055.000 | 7 |
| Diferencia de edad con la pareja (diferencia_edad_pareja) | 8579 | -81.000 | -4.000 | -1.000 | 2.000 | 48.000 | -13.000 | 11.000 | 502 |

## Revisión temporal bajo hipótesis

| revision | registros |
| --- | --- |
| Fecha ausente | 0 |
| Texto de Fecha registrada en la base (fecha) no interpretable | 0 |
| Fecha fuera de 2022–2023 | 0 |
| Si Fecha registrada en la base (fecha) fuera la referencia: inicio posterior a Fecha registrada en la base (fecha) | 0 |
| Si Fecha registrada en la base (fecha) fuera la referencia: duración supera edad de la persona | 0 |
| Si Fecha registrada en la base (fecha) fuera la referencia: duración supera edad de la pareja | 8 |

## Perfil del archivo procesado

| Variable (nombre y código) | tipo | faltantes | Porcentaje de faltantes |
| --- | --- | --- | --- |
| Dependencia económica de la pareja (p93) | category | 77 | 0.898 |
| Valoración de la vida sexual (i_6_p9) | category | 105 | 1.224 |
| Bienestar mental o emocional percibido (i_2_p9) | category | 11 | 0.128 |
| Edad de la persona encuestada (p4) | Int64 | 0 | 0.000 |
| Sexo asignado al nacer (p1) | category | 0 | 0.000 |
| Género declarado (p3) | category | 3 | 0.035 |
| Nivel educacional (p5) | category | 0 | 0.000 |
| Región (region) | category | 0 | 0.000 |
| Estado conyugal o civil (p7) | category | 5 | 0.058 |
| Ingreso relativo respecto de la pareja (p92) | category | 170 | 1.982 |
| Año de inicio de convivencia (p84) | Int64 | 0 | 0.000 |
| Edad de la pareja (p91) | Int64 | 0 | 0.000 |
| Actividad sexual con la pareja en el último mes (p96) | category | 445 | 5.187 |
| Salud general percibida (p10) | category | 50 | 0.583 |
| Calidad de vida percibida (p8) | category | 17 | 0.198 |
| Tiene pareja actualmente (p81) | category | 0 | 0.000 |
| Convive actualmente con su pareja (p83) | category | 0 | 0.000 |
| Identificador de la encuesta (folio_encuesta) | string | 0 | 0.000 |
| Fecha registrada en la base (fecha) | datetime64[us] | 0 | 0.000 |
| Diferencia de edad con la pareja (diferencia_edad_pareja) | Int64 | 0 | 0.000 |
| Años aproximados de convivencia (anios_convivencia_aprox) | Int64 | 8579 | 100.000 |

## Límites y continuidad

La varianza de códigos en los escenarios de imputación es un diagnóstico mecánico de sensibilidad; no demuestra que las escalas ordinales tengan intervalos iguales. Las señales temporales calculadas bajo la hipótesis de que fecha fuera la referencia tampoco confirman errores por sí solas. Los casos extremos permanecen para revisión y análisis de sensibilidad en F3.

## Ubicación de los productos

Los CSV se generan en F1/data/processed. La configuración y el diccionario están en F2/docs/esquema_variables_F2.json y Diccionario_procesado_F2.md. La bitácora y validacion_F2.json permiten contrastar estas cifras con las salidas del notebook.
