# Selección de variables de ENSSEX

## Por qué seleccionamos estas 19 columnas

La pregunta necesita identificar a las personas que conviven con su pareja y comparar dos valoraciones de bienestar entre los niveles de dependencia económica. Ese es el núcleo del estudio. Conservamos además datos que permiten describir a esas personas, contextualizar futuras comparaciones y comprobar la calidad de los registros.

La selección se organiza por su utilidad concreta:

- **3 centrales:** una define los grupos de dependencia económica y dos registran las valoraciones que se compararán por separado.
- **12 complementarias:** describen el contexto sociodemográfico, de la relación y de salud. Su conservación permite evaluar análisis posteriores sin volver a seleccionar datos del archivo completo.
- **4 auxiliares:** dos definen quién pertenece a la población, una identifica cada registro y una permite revisar una posible referencia temporal.

**No todas las 19 columnas son necesarias en cada comparación.** Para delimitar la población y abordar la pregunta básica utilizamos las tres centrales y los dos filtros de pareja y convivencia. Las demás cumplen una función de contexto o de control técnico. No se eligieron porque ya hayan demostrado una asociación con el bienestar ni porque deban entrar juntas en un modelo. Cada uso posterior dependerá de su pertinencia y de la calidad de las respuestas.

Las tablas indican la pregunta asociada, con ajustes menores de redacción ya documentados en F1. Región, identificador y fecha son campos de la base; no se presentan como preguntas numeradas al encuestado. El código se mantiene entre paréntesis para poder localizar cada columna en el archivo.

### Centrales: qué comparamos y entre qué grupos

| Variable y código | Pregunta o nombre del dato | Por qué la conservamos |
| --- | --- | --- |
| Dependencia económica de la pareja (p93) | ¿Diría que usted depende económicamente de su pareja? | Define los tres grupos que se compararán: dependencia completa, parcial y ausencia de dependencia. Es la variable explicativa de la pregunta; no equivale al monto de ingresos ni demuestra una relación causal. |
| Valoración de la vida sexual (i_6_p9) | P9: valorar de 1 a 7 cómo se siente en distintos ámbitos. Ítem: «Con su vida sexual». | Registra una de las dos valoraciones que queremos comparar entre niveles de dependencia. Describe cómo la persona valora su vida sexual; no se sustituye por la presencia de actividad sexual ni se suma al bienestar emocional. |
| Bienestar mental o emocional percibido (i_2_p9) | P9: valorar de 1 a 7 cómo se siente en distintos ámbitos. Ítem: «Con su bienestar mental o emocional». | Registra la segunda valoración de la pregunta. Permite estudiar este ámbito por separado de la vida sexual. Es una percepción declarada por la persona, no un diagnóstico de salud mental. |

### Complementarias: características sociodemográficas

| Variable y código | Pregunta o nombre del dato | Por qué la conservamos |
| --- | --- | --- |
| Edad de la persona encuestada (p4) | ¿Qué edad tiene? (años). | Permite describir la composición por edad de los grupos de dependencia y evaluar comparaciones por etapas de vida. También es necesaria para calcular la diferencia de edad con la pareja. |
| Sexo asignado al nacer (p1) | ¿Cuál es su sexo asignado al nacer? | Permite caracterizar a las personas y explorar, si los datos lo permiten, si los patrones descriptivos difieren según el sexo asignado al nacer. Se conserva separado del género declarado porque son preguntas distintas. |
| Género declarado (p3) | ¿Cuál es el género con el que usted se identifica? | Permite describir cómo se identifican las personas sin deducir su género a partir del sexo asignado al nacer. Su uso en comparaciones posteriores dependerá del número de respuestas disponibles en cada categoría. |
| Nivel educacional (p5) | ¿Cuál es su nivel educacional más alto alcanzado o su nivel educacional actual? | Aporta contexto educativo a la composición de los grupos. Puede servir para caracterizar sus diferencias en fases posteriores; no se usa como sustituto de ingreso ni se impone un orden a modalidades educativas heterogéneas. |
| Región (region) | Región registrada en la base; no es una pregunta numerada del cuestionario. | Permite describir la composición territorial de la muestra y evaluar comparaciones por contexto geográfico. Conservarla no implica que este análisis sin ponderación produzca estimaciones representativas de cada región. |
| Estado conyugal o civil (p7) | ¿Cuál es su estado conyugal o civil actual? | Permite distinguir situaciones civiles entre quienes efectivamente conviven con su pareja. Aporta contexto de la relación; no reemplaza las preguntas que identifican si la persona tiene pareja y vive con ella. |

### Complementarias: relación de pareja y salud

| Variable y código | Pregunta o nombre del dato | Por qué la conservamos |
| --- | --- | --- |
| Ingreso relativo respecto de la pareja (p92) | Comparando con su pareja actual, el ingreso económico de usted es… | Complementa la dependencia declarada con la posición de ingresos frente a la pareja. Tener ingresos menores y depender económicamente no son respuestas equivalentes. Se conserva también la categoría sin ingresos propios. |
| Año de inicio de convivencia (p84) | ¿Desde qué año viven juntos? Se aplica a quienes declaran convivir con su pareja. | Describe desde cuándo conviven y permite preparar una duración aproximada de la relación. Se conserva el año original, aunque esa duración no se calcula mientras falte validar una fecha de referencia. |
| Edad de la pareja (p91) | ¿Qué edad tiene esa pareja? Edad en años cumplidos. | Aporta contexto de la relación y, junto con la edad de la persona encuestada, permite calcular la diferencia de edad. Se usa lo declarado por la persona; no es una segunda entrevista a su pareja. |
| Actividad sexual con la pareja en el último mes (p96) | En el último mes, ¿tuvo relaciones sexuales con su pareja? | Permite contextualizar la valoración de la vida sexual según la presencia de actividad reciente con la pareja. No mide satisfacción ni frecuencia, por lo que se conserva como una dimensión distinta del resultado principal. |
| Salud general percibida (p10) | En general, usted diría que su salud es… | Aporta una descripción del estado de salud general percibido para contextualizar ambos resultados. No se interpreta como causa de las valoraciones ni reemplaza la pregunta específica sobre bienestar mental o emocional. |
| Calidad de vida percibida (p8) | ¿Cómo calificaría su calidad de vida? | Permite situar las dos valoraciones específicas dentro de una apreciación más amplia de la vida. Se conserva para análisis complementarios; no se combina con ellas para construir un indicador único. |

### Auxiliares: población y trazabilidad

| Variable y código | Pregunta o nombre del dato | Por qué la conservamos |
| --- | --- | --- |
| Tiene pareja actualmente (p81) | Actualmente, ¿usted tiene pareja? | Identifica a las personas que declaran una pareja actual. Es el primer filtro de la población y debe aplicarse junto con la convivencia con esa pareja; tener pareja por sí solo no garantiza convivencia. |
| Convive actualmente con su pareja (p83) | ¿Y actualmente usted vive con esa pareja? Se aplica a quienes responden 1 en P81. | Identifica la convivencia con la pareja actual. Junto con la pregunta sobre existencia de pareja, delimita exactamente la población de la investigación. Después del filtro se conserva como comprobación, no como predictor variable. |
| Identificador de la encuesta (folio_encuesta) | Identificador de la encuesta; no es una pregunta sustantiva. | Permite comprobar que cada registro esté identificado, detectar duplicados y vincular la base preparada con el original. Su número no representa una característica de la persona y no se utiliza en promedios ni modelos. |
| Fecha registrada en la base (fecha) | Fecha registrada en la base; el libro de códigos no desarrolla su significado y el SAV no aporta una etiqueta descriptiva. | Se conserva para revisar una posible referencia temporal y comprobar coherencia con el inicio de convivencia. Las fuentes no definen qué evento representa; por eso su inclusión no autoriza a calcular años de convivencia ni a asumir que es la fecha de entrevista. |

### Qué aporta esta selección a las siguientes fases

En F2 comprobamos la disponibilidad y calidad de estas columnas. En F3 podremos comparar cada valoración entre los grupos de dependencia, describir la composición de esos grupos y evaluar análisis por características personales o de la relación, siempre que existan suficientes respuestas válidas. Conservar una columna no la convierte automáticamente en una causa, un predictor o una variable de ajuste obligatoria.

La edad de la persona encuestada (p4) y la edad de su pareja (p91) permiten calcular la diferencia de edad. El año de inicio de convivencia (p84) y la fecha registrada (fecha) permitirían calcular una duración aproximada solo si se confirma una referencia temporal válida. Por eso conservamos esos datos, pero los años de convivencia permanecen sin calcular. Estas dos derivadas se explican aparte de las 19 columnas originales.

