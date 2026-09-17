# MCDI500 · Grupo 9 · ENSSEX

Proyecto de Programación para la Ciencia de Datos de la Universidad Andrés Bello.

Nuestro tema de trabajo es el bienestar y la calidad de vida a partir de los datos de ENSSEX 2022–2023.

## Integrantes

- Guillermo Osorio Zamora — [gosoriozamora](https://github.com/gosoriozamora)
- Karla Patricia Pizarro Correa — [KarlaPPC](https://github.com/KarlaPPC)

## Organización del proyecto

En este repositorio reuniremos el trabajo de las fases 1 y 2 para la Sumativa 1. Mantendremos esta base para continuar después con las fases 3 y 4.

```text
proyecto-enssex/
├── README.md
├── requirements.txt
├── .gitignore
├── F1/
│   ├── README.md
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── notebooks/
│   ├── src/
│   └── docs/
├── F2/
│   ├── README.md
│   ├── notebooks/
│   └── docs/
├── F3/
├── F4/
└── docs/
```

- **F1:** definición del problema, objetivos, preparación del entorno y primera revisión de los datos.
- **F2:** obtención, exploración, limpieza, transformación y comprobación de los datos.
- **F3 y F4:** espacios reservados para las siguientes fases del curso.
- **docs, en la raíz:** informe integrado de la Sumativa 1 y sus anexos.

Las carpetas `F1/data` y `F1/src` se utilizarán también en las fases posteriores, siguiendo la organización de la guía del curso y de nuestro mapa conceptual. F2 guardará los datos que procese en `F1/data/processed`; el código y las explicaciones de esa fase estarán identificados en F2.

Conservamos una copia de la Formativa 1, sin cambios, en [F1/docs/Formativa1_Grupo9.pdf](F1/docs/Formativa1_Grupo9.pdf). El informe de la Sumativa 1 se preparará como un documento nuevo en [docs](docs/README.md).

Por ahora, contamos con la estructura del repositorio y una validación preliminar en F1. Los notebooks finales y el informe de la Sumativa 1 están pendientes.

Los archivos `.gitkeep` permiten conservar en Git las carpetas que aún no tienen contenido. No forman parte del análisis.

## Datos y ejecución

Trabajaremos con ENSSEX 2022–2023. Para la revisión preliminar se utilizó un archivo CSV convertido desde el formato SAV.

Registramos las bibliotecas instaladas en `requirements.txt`, a partir del entorno actual de Windows con Python 3.13.15. La comprobación de dependencias no detectó conflictos. Este archivo se actualizará si el desarrollo requiere otras bibliotecas.

Nos falta completar las instrucciones para obtener los datos, realizar la conversión e instalar el entorno desde una copia nueva del repositorio. También probaremos los notebooks en ambos computadores para comprobar que podemos obtener los mismos resultados.

Los datos originales y el entorno virtual se mantienen fuera de esta versión del repositorio.

## Trabajo en equipo

Ambos integrantes guardaremos nuestros cambios desde nuestras propias cuentas de GitHub. Los mensajes de cada commit describirán el aporte realizado, para que podamos seguir el avance del trabajo y revisar los cambios.

## Trabajo pendiente

- Definir la pregunta de investigación y los objetivos.
- Seleccionar las variables y explicar su significado.
- Completar los notebooks de F1 y F2 y guardar sus resultados.
- Explicar las decisiones de limpieza y transformación.
- Probar el código con datos habituales y con situaciones que puedan producir errores.
- Revisar los resultados de cada etapa.
- Documentar las bibliotecas necesarias y los pasos de ejecución.
- Preparar el informe, relacionar el trabajo con el mapa conceptual e incorporar las referencias.
- Comprobar que el docente pueda acceder al repositorio.
