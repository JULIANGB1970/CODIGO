import pandas as pd
import numpy
import re
from collections import  Counter



def remove_accents(old):
   
    new = old.lower()

    new = re.sub(r'[àáâãäå]', 'a', new)
    new = re.sub(r'[èéêë]', 'e', new)
    new = re.sub(r'[ìíîï]', 'i', new)
    new = re.sub(r'[òóôõö]', 'o', new)
    new = re.sub(r'[ùúûü]', 'u', new)
    new= re.sub(r'[^\w\s]', " ", new)
    return new





#leo el callejero de Zaragoza
df_ayto= pd.read_excel(".content\\CALLEJERO_2022.xlsx")

#convierto el contenido de las rows en la columna NOMBRE LITERAL en una lista de string
texting = df_ayto['NOMBRE LITERAL'].str.split()

print(texting.head(10))
corpus=[[word for word in elem] for elem in texting if elem]

#creo un corpus para poder analizar la frecuencia de las palabras
corpux = [remove_accents(item) for row in corpus for item in row ]



counter=Counter(corpux)
most=counter.most_common()
df_common = pd.DataFrame()

x, y= [], []
for word,count in most:

    x.append(word.strip())
    y.append(count)

df_common['token'] = x
df_common['ocurrencias'] = y


#guardo todas aquellas palabras que aparecen una única vez en todos los términos del callejero zaragozano
df_common[df_common['ocurrencias']== 1].to_excel("terminos.xlsx")





print(df_ayto['TIPO DE VÍA'].unique())


#después de seleccionar, entre las que aparecen una única vez las palabras que servirán como claves, procedo a actualizar datos.
df_correg = pd.read_excel(".\\terminos_unicos.xlsx")

#creo dos columnas nuevas para guardar la dirección encontrada y el cp
df_correg['direccion']=""
df_correg['CP'] = ""


#este es un diccionario con la traducción de los tipos de via que aparacen en el callejero
tipos_dict ={'CL': 'Calle',  'CN': 'Camino', 'AN': 'Andador', 'PL': 'Plaza', 'GL': 'Glorieta', 'CR ': 'Carretera', 'RD': 'Ronda', 'JR': 'Jardin', 'PS': 'Paseo', 'AV': 'Avenida', 'UR': 'Urbanizacion', 'PQ': 'Parque', 'PT': 'Puente', 'VI': 'Via',
 'CJ': 'Callejon', 'EB': 'Embarcadero', 'RT': 'Rotonda', 'BLV': 'Bulevar', 'CR': 'Carrera', 'SOTO': 'Soto', 'PG': 'Poligono', 'GP': 'Grupo', 'PJ': 'Pasaje', 'TR': 'Travesia', 'LG': 'Lago', 'BR': 'Barrio', 'RC': 'Rincon', 'PA': 'Patio'}


#creo una lista con todos los barrios excpeto el primero que toma valor nana
barrios_rurales = df_ayto['BARRIO RURAL'].unique().tolist()[1:]
print(barrios_rurales)

barrios_rurales = '|'.join(barrios_rurales)

#este es un diccionario con la traducción de las siglas de los barrrios rurales que aparacen en el callejero
br = {'MNT': 'Montañana', 'SIS': 'Santa Isabel', 'CRT': 'Cartuja Baja', 'GRP': 'Garrapinillos', 'SJN': 'San Juan de Mozarrifar', 'TRC': 'Torrecilla de Valmadrid', 'CST': 'Casetas', 'MVR': 'Movera', 'VNO': 'Venta del Olivar', 'JSL': 'Juslibol',
 'MNZ': 'Monzalbarba', 'PÑF': 'Peñaflor', 'ALF': 'Alfocea', 'SGR': 'San Gregorio', 'VLR': 'Villarrapa', 'MRL': 'Miralbueno'}

#aqui voy a buscar las "palabras clave" obtenidas del callejero y voy a extraer el nombre completo de la calle, el barrio rural y el código postal
for index, row in df_correg .iterrows():

    if row['sino']:

        termino =  "\\b" + row["token"].strip() +"\\b" 
        

        for inde, ro in df_ayto .iterrows():
            
            buscar_en = remove_accents(ro["NOMBRE LITERAL"])
            buscar_en = re.sub(barrios_rurales," ", buscar_en).strip()


            if re.search(termino, buscar_en):
               
                tipo = ro['TIPO DE VÍA']
                barrio_ru = ""
                try:
                    barrio_ru = br.get(ro['BARRIO RURAL'])
                    if barrio_ru == None: barrio_ru =""
                except:
                     pass

                nombre_tipo = tipos_dict.get(tipo)
                



                df_correg.loc[index, 'direccion'] = nombre_tipo.lower() + " " + buscar_en + " " + barrio_ru
                df_correg.loc[index, 'CP'] = ro['CÓDIGO POSTAL']
                print(row["token"].strip() , nombre_tipo + " " + buscar_en + " " + barrio_ru)

            else:
                pass

    else:
         continue



df_correg.CP =df_correg.CP.str.replace(r'[^\w\s]', '')
df_correg.to_excel("corregidos.xlsx")

     

