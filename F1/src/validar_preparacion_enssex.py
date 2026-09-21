"""Casos controlados para comprobar las reglas analíticas de F2."""
import pandas as pd
from preparar_enssex import (
    normalizar_variable, limpiar_codigos, seleccionar_convivientes,
    tipificar_categorias, construir_derivadas, codificar_nominales,
    resumen_atipicos, comparar_imputaciones, validar_columnas,
    validar_resultado,
)


def ejecutar_pruebas(esquema):
    specs = {v['nombre']: v for v in esquema['variables']}
    evidencia = []

    def caso(nombre, comprobar):
        comprobar()
        evidencia.append({'caso': nombre, 'resultado': 'OK'})

    def iguales(nombre, entrada, esperado):
        resultado = normalizar_variable(pd.Series(entrada), specs[nombre])
        assert resultado.fillna(-9999).tolist() == [(-9999 if x is None else x) for x in esperado]

    def error_esperado(funcion, contiene):
        try:
            funcion()
        except ValueError as error:
            assert contiene in str(error), str(error)
        else:
            raise AssertionError('No se detectó la entrada incorrecta.')

    caso('Región 8 y 9 son válidas', lambda: iguales('region', [8,9], [8,9]))
    caso('Estado civil 8 válido, 88/99 ausentes', lambda: iguales('p7', [8,88,99], [8,None,None]))
    caso('Ingreso relativo 6 válido, 8/9 ausentes', lambda: iguales('p92', [6,8,9], [6,None,None]))
    caso('Edad de pareja 99 válida; 999 es NS/NR', lambda: iguales('p91', [99,999], [99,None]))
    caso('Género 7, 8 y 9 son no respuesta', lambda: iguales('p3', [1,6,7,8,9], [1,6,None,None,None]))
    caso('Año 9999 es no respuesta', lambda: iguales('p84', [2000,9999], [2000,None]))
    caso('Escala 1–7 admite extremos, recodifica 9', lambda: iguales('i_6_p9', [1,7,9], [1,7,None]))
    caso('Escala 1–7 rechaza código 8', lambda: error_esperado(
        lambda: normalizar_variable(pd.Series([8]), specs['i_6_p9']), 'Categoría'))
    caso('Edad rechaza texto inesperado', lambda: error_esperado(
        lambda: normalizar_variable(pd.Series(['error']), specs['p4']), 'Tipo inesperado'))
    caso('Edad rechaza valores fraccionarios', lambda: error_esperado(
        lambda: normalizar_variable(pd.Series([25.5]), specs['p4']), 'enteros'))
    caso('Fecha imposible se detecta', lambda: error_esperado(
        lambda: normalizar_variable(pd.Series(['30/02/2022']), specs['fecha']), 'día/mes/año'))
    caso('Tabla vacía se detecta', lambda: error_esperado(
        lambda: validar_columnas(pd.DataFrame(columns=['p81']), ['p81']), 'No hay registros'))
    caso('Columna ausente se detecta', lambda: error_esperado(
        lambda: validar_columnas(pd.DataFrame({'p81':[1]}), ['p81','p83']), 'Faltan columnas'))
    caso('Nombres duplicados se detectan', lambda: error_esperado(
        lambda: validar_columnas(pd.DataFrame([[1,1]],columns=['p81','p81']), ['p81']), 'repetidos'))

    fila = {'p93':1,'i_6_p9':7,'i_2_p9':6,'p4':40,'p1':1,'p3':1,'p5':9,
            'region':8,'p7':8,'p92':6,'p84':2010,'p91':37,'p96':1,'p10':4,
            'p8':4,'p81':1,'p83':1,'folio_encuesta':101,'fecha':'1/08/2022'}
    def filtro_y_copia():
        base=pd.DataFrame([fila,dict(fila,p81=2,folio_encuesta=102),
                           dict(fila,p83=2,folio_encuesta=103)])
        copia=base.copy(deep=True)
        seleccion,_=seleccionar_convivientes(base,esquema)
        assert len(seleccion)==1 and seleccion.folio_encuesta.iloc[0]==101
        seleccion.loc[seleccion.index[0],'p4']=99
        pd.testing.assert_frame_equal(base,copia)
    caso('Ambos filtros son necesarios; la copia no modifica la base', filtro_y_copia)
    caso('Folios repetidos detienen la selección', lambda: error_esperado(
        lambda: seleccionar_convivientes(pd.DataFrame([fila,fila]),esquema), 'folios'))
    caso('Selección sin convivientes se detecta', lambda: error_esperado(
        lambda: seleccionar_convivientes(pd.DataFrame([dict(fila,p83=2)]),esquema), 'Ninguna'))

    def categorias_derivadas():
        datos=pd.DataFrame([fila,dict(fila,p93=9,p3=7,folio_encuesta=102,p4=30,p91=40)])
        copia=datos.copy(deep=True)
        limpia,_=limpiar_codigos(datos,esquema)
        final=tipificar_categorias(construir_derivadas(limpia),esquema)
        assert final.diferencia_edad_pareja.tolist()==[3,-10]
        assert final.anios_convivencia_aprox.isna().all()
        assert final.p93.cat.ordered and final.p93.cat.categories.tolist()==[1,2,3]
        assert not final.region.cat.ordered
        matriz=codificar_nominales(final,esquema)
        assert matriz['p3__sin_respuesta'].tolist()==[0,1]
        assert matriz.filter(regex='^p3__').sum(axis=1).eq(1).all()
        pd.testing.assert_frame_equal(datos,copia)
    caso('Orden, derivadas, NA y one-hot conservan el significado', categorias_derivadas)

    def cambio_no_autorizado():
        datos=pd.DataFrame([fila])
        limpia,_=limpiar_codigos(datos,esquema)
        final=tipificar_categorias(construir_derivadas(limpia),esquema)
        final.loc[0,'p4']=41
        matriz=codificar_nominales(final,esquema)
        try:
            validar_resultado(datos,final,matriz,esquema)
        except AssertionError as error:
            assert 'Respuestas sustantivas conservadas en p4' in str(error)
        else:
            raise AssertionError('No detectó una edad cambiada sin justificación.')
    caso('Cambio de una respuesta válida es detectado', cambio_no_autorizado)

    def limite_sin_faltantes():
        datos=pd.DataFrame({'p93':pd.Series([1,1,1],dtype='Int64'),
                            'i_6_p9':pd.Series([7,7,7],dtype='Int64')})
        atip=resumen_atipicos(datos,['i_6_p9'])
        assert atip.senalados_IQR.iloc[0]==0
        opciones=comparar_imputaciones(datos,['i_6_p9'])
        assert opciones.imputados.eq(0).all() and opciones.cambio_varianza_pct.eq(0).all()
    caso('Una categoría, sin nulos y varianza cero', limite_sin_faltantes)

    def limite_todos_nulos():
        resultado=normalizar_variable(pd.Series([9,9]),specs['i_6_p9'])
        assert resultado.isna().all()
        resumen=resumen_atipicos(pd.DataFrame({'x':resultado}),['x'])
        assert resumen.n.iloc[0]==0
    caso('Columna completamente ausente se conserva como tal', limite_todos_nulos)
    return pd.DataFrame(evidencia)
