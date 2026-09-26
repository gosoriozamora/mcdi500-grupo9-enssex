"""Alternativas didácticas sobre edades ya limpiadas y validadas con F2."""
import pandas as pd


def validar_edades(tabla):
    """Comprueba estructura y tipo; las reglas de edades proceden de F2."""
    if not isinstance(tabla, pd.DataFrame):
        raise TypeError('La entrada debe ser un DataFrame.')
    if not tabla.columns.is_unique:
        raise ValueError('No se admiten columnas duplicadas.')
    for nombre in ('p4', 'p91'):
        if nombre not in tabla.columns:
            raise ValueError(f'Falta la columna {nombre}.')
        if tabla[nombre].dtype != pd.Int64Dtype():
            raise TypeError(f'{nombre} debe tener tipo Int64, después de limpiar con F2.')


def diferencia_con_bucle(tabla):
    """Resta las edades por posición; si falta alguna, conserva la ausencia."""
    validar_edades(tabla)
    diferencias = []
    for edad, edad_pareja in zip(tabla['p4'], tabla['p91']):
        if pd.isna(edad) or pd.isna(edad_pareja):
            diferencias.append(pd.NA)
        else:
            diferencias.append(edad - edad_pareja)
    return pd.Series(diferencias, index=tabla.index, dtype='Int64',
                     name='diferencia_edad_pareja')


def diferencia_por_columnas(tabla):
    """Aplica la resta por columnas utilizada por construir_derivadas de F2."""
    validar_edades(tabla)
    return (tabla['p4'] - tabla['p91']).astype('Int64').rename('diferencia_edad_pareja')
