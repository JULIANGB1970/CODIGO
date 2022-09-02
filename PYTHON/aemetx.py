from aemet import Aemet, Estacion
import json
import time
import requests
import pandas as pd
import numpy as np
import os
from datetime import date

#Este es un programilla para bajarse los datos de aemet para una o más estaciones metereológigas (si los hay)
#se necesita una clave que se puede obtener de forma gratuita
#https://opendata.aemet.es/centrodedescargas/altaUsuario


apikey = 'tu clave'


aemet = Aemet('tu clave')

estaciones = Estacion.get_estaciones('tu clave')

dfestaciones = pd.DataFrame.from_records(estaciones)

cadena =input("Ponme un nombre de estación:")

indx =  dfestaciones.loc[dfestaciones['nombre'].str.contains(cadena, case=False)]
indy= indx[['nombre','indicativo']]

print("Datos de las siguientes estaciones: ")

print(indy['nombre'])

print('XXXXXXXXXXXXXXXXXXXXXXXXX')

def datox(dframe):
    today = date.today()
    fecha_final =  today.strftime("%Y-%m-%d") + "T00:00:00UTC"
    lista = []
    aviso=""
    dftmp = pd.DataFrame()
    dfdef = pd.DataFrame()
    for index, indic in dframe.iterrows():

        vcd = aemet.get_valores_climatologicos_diarios("2022-01-01T00:00:00UTC",fecha_final, indic['indicativo'])
        str_match = list(filter(lambda x: 'descripc' in x, vcd))
        
        if len(str_match)==0: 
               
                if len(dfdef.index) == 0 :
                    
                    dfdef = pd.DataFrame.from_records(vcd)
                   
                else:
                    
                    
                    dftmp = pd.DataFrame.from_records(vcd)
                    dfdef = pd.concat([dfdef, dftmp],axis = 0)         
                   
        else:
            print( "Faltan datos para la estación: ", indic['nombre'])
            str_match=[]
    return(dfdef)
    
    






dfexcel =datox(indy)
writer = pd.ExcelWriter(r'data.xlsx', engine = 'openpyxl', mode ='w')
dfexcel.to_excel(writer, sheet_name ='DATOS METEREOLÓGICOS')
writer.save()
os.startfile(r'data.xlsx')





