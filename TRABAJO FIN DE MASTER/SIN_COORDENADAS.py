import pandas as pd
import numpy
import os
import re
import itertools
import time
from collections import  Counter
import unidecode
import IPython
import os
import geocoder
import stanza

'''
Con este código lo que voy a hacer por un lado es utilizar la variable stanza para tratar de extraer las direcciones
del título y la descripción de la queja.

Por otro, buscar esas direcciones, por medio de la librería RE, las palabras únicas que identificana a cada calle y el propio callejero.

A la vez, actualizaremos el código postal para los lugares que vayamos encontrando.

'''








#descargo el modelo de palabras para castellano de stanza
stanza.download('es') 

nlp = stanza.Pipeline(lang='es', processors='tokenize,ner')



     

def remove_accents(old):
   
    new = old.lower()

    new = re.sub(r'[àáâãäå]', 'a', new)
    new = re.sub(r'[èéêë]', 'e', new)
    new = re.sub(r'[ìíîï]', 'i', new)
    new = re.sub(r'[òóôõö]', 'o', new)
    new = re.sub(r'[ùúûü]', 'u', new)
    new= re.sub(r'[^\w\s]', " ", new)
    return new






def extraer_direccion(cadena):
    doc = nlp(cadena)
    direcciones_dict = [ent.to_dict() for ent in doc.ents if ent.type=="LOC"]
    direcciones =  [direccion.get("text") for direccion in direcciones_dict]
    direcciones_str = ','.join(direcciones)
    print(direcciones_str)
   
    return direcciones_str





#cargo el df_test sin las predicciones y hago un merge por service_request_id para tener el df_test tratado y las predicciones en la misma dataframe
df1 = pd.read_excel(".\\content\\df_test.xlsx")
df2 = pd.read_excel(".\\content\\resultados.xlsx")
df2.rename(columns={'service_name': 'service_name_predict' }, inplace = True)

df2 = df2[['service_request_id', 'predict', 'service_name_predict' ]]

print(len(df1))
df = pd.merge(df1, df2, how="left", on = "service_request_id")
print(len(df))
print(df.columns)
#cargo el callejero
df_ayto= pd.read_excel(".\\content\\CALLEJERO_2022.xlsx")


#elijo todos aquellos registros en la que los usuarios no han incluido su dirección
df_sin_direccion = df[df.address_string.isnull()]
#y los que si la tienen
df_con_direccion = df[~df.address_string.isnull()]

#traduzo nomenclatura de callejero a sus correspondientes términos
tipos_dict ={'CL': 'Calle', 'CT': 'Carretera', 'CN': 'Camino', 'AN': 'Andador', 'PL': 'Plaza', 'GL': 'Glorieta', 'CR ': 'Carretera', 'RD': 'Ronda', 'JR': 'Jardin', 'PS': 'Paseo', 'AV': 'Avenida', 'UR': 'Urbanizacion', 'PQ': 'Parque', 'PT': 'Puente', 'VI': 'Via',
 'CJ': 'Callejon', 'EB': 'Embarcadero', 'RT': 'Rotonda', 'BLV': 'Bulevar', 'CR': 'Carrera', 'SOTO': 'Soto', 'PG': 'Poligono', 'GP': 'Grupo', 'PJ': 'Pasaje', 'TR': 'Travesia', 'LG': 'Lago', 'BR': 'Barrio', 'RC': 'Rincon', 'PA': 'Patio'}



#ahora junto el contenido del campo titulo y el de descripción para ampliar las posibilidades de encontrar la dirección exacta
df_sin_direccion["title_description"]  =  df_sin_direccion["title"] + " "+ df_sin_direccion["description"]


#aplico el NER de la librería stanza, generando un campo con los resultados obtenidos por la misma
df_sin_direccion['direccion_stanza'] = df_sin_direccion.title_description.apply(lambda x: extraer_direccion(x))


#creo dos nuevas columnas para almacenar el CP y la dirección que obtengamos a continuación
df_sin_direccion['CÓDIGO POSTAL']= ""
df_sin_direccion['direccion_callejero']= ""
print(df_sin_direccion.columns)


#leo claves únicas
df_callejero =pd.read_excel(".\\content\\corregidos.xlsx")

total = 0
encontradas = 0

for index, row in df_sin_direccion.iterrows():
    
    clasificada = False
    total = total + 1
    row_descripcion = row['title_description'] 
    
    


         
    
    #busco la palabra por términos únicos
    for inde, ro in df_callejero.iterrows():
                            


        
                            if ro['sino'] == True and len(ro['token'])>3:
                                buscar_en = remove_accents(row_descripcion)
               
                                try:
                                    cabecera = ro['direccion'][0:2]
                                except:
                                    pass
                
                            #aplico la libreria RE
                                termino =  "\\s*(" + cabecera + "){1}\\w+\\s+(de)*\\s*"  + ro['token'] +  "+\\W*\\s*"
                              
                                
                               
                            
                                if re.search(termino, buscar_en):
                

                                    encontradas = encontradas + 1
                                    df_sin_direccion.loc[index, 'direccion_callejero'] = ro['direccion']
                                    df_sin_direccion.loc[index, 'CP'] = ro['CP']
                                    
                                    print( cabecera + " " + termino, "   ", ro['direccion'] , "UNICAS")
                                    clasificada = True
                                    break
                       

    

    #busco la palabra en el callejero
    if clasificada == False:
    
    
        for ayto_inde, ayto_ro in df_ayto.sort_values(by='NOMBRE LITERAL', ascending=False, key=lambda x: x.str.len()).iterrows():


                buscar_en = remove_accents(row_descripcion)        
                tipo = ayto_ro['TIPO DE VÍA']
    
                try:
                    via = tipos_dict.get(tipo)[0:2]
                except:
                    via = ""
                
                termino =  "\\s*(" + via.lower() + "){0,1}\\w*\\s*(de)*\\s*\\b"  + remove_accents(ayto_ro['NOMBRE LITERAL']) +  "\\b"
                
                if re.search(termino, buscar_en):
                        clasificada = True
                            
                        encontradas = encontradas + 1
                        df_sin_direccion.loc[index, 'direccion_callejero'] = tipos_dict.get(tipo) + " " + ayto_ro['NOMBRE LITERAL']
                        df_sin_direccion.loc[index, 'CP'] =  ayto_ro['CÓDIGO POSTAL']
                        print( termino, ayto_ro['NOMBRE LITERAL'],  "CALLEJERO" )
                        break






                

                    

    print(df_sin_direccion.columns)                   

    if clasificada == False: 
       
        print("No se pudo obtener la dirección")      


    print(total, encontradas, round(encontradas/total,2))               
    print("\n"*5)




#df_sin_coordenadas= pd.concat([df_sin_direccion,df_con_direccion], axis = 0)
#df_sin_coordenadas.to_excel(".\\content\\sin_coordenadas.xlsx")

df_sin_direccion.to_excel(".\\content\\sin_direccion_sin_coord.xlsx")
df_con_direccion.to_excel(".\\content\\con_direccion_sin_coord.xlsx")
