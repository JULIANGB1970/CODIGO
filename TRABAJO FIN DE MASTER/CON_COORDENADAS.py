import pandas as pd
import os
import geopandas
import numpy as np
import time
import re


'''
Con este código lo que hago es introducir en el geocoder la dirección extraida por medio de la libreria RE
obteniendo las coordenadas.

Por otro lado, cuando existen coordenadas en la queja, pero no existe address_string, la dirección física,
hago un reverse geocoding para obtenerla dandole a Google la latitud y la longitud.


'''




os.environ["GOOGLE_API_KEY"] = ""

import geocoder


def obtener_direccion(cadena, modo):
    
    loc = ""
    

    #en este modo busco coordenadas introduciendo el texto de la dirección extraida por RE
    if modo == 'anverso':
    
        try:
          
            print("la direccion es:", cadena)
            dir = cadena + ', Zaragoza, Aragón, España'
            print(dir)
            locx = geocoder.google(dir)
            loc = locx[0]
        
            print(loc)             
            if loc.latlng != [41.6488226, -0.8890853]:
                    
                print(loc)
                print(loc.latlng)
                print("\n\n\n\n\n")
            else:
                print("nothing")
   
        except Exception as error:
            print(error)
            pass
            
            print(cadena, loc)
    else:
    #en este modo obtengo la dirección física por medio de las coordenadas pasadas a Google        
            locx = geocoder.google(cadena, method='reverse')
            loc = locx[0]
    
    
    
    return loc



df1 = pd.read_excel(".//content/con_direccion_sin_coord.xlsx")
df2 =  pd.read_excel(".//content/sin_direccion_sin_coord.xlsx")

df = pd.concat([df1, df2], axis = 0)



for index, row in df.iterrows():

        if pd.isna(row['address_string']):
        
                df.loc[index, 'address_string']    = row['direccion_callejero'] 

        else:

            pass


#elimino el simbolo que aparece en algunos registros
df.CP = df.CP.replace('\+','', regex=True)









for index, row in df.iterrows():
    cp = ""
    lat= ""
    long = ""
    address= ""
    codigop = ""
    print(row["service_request_id"])

    
    
    if pd.isna(row['long']):
        
        
        if not(pd.isna(row['address_string'])):
            address = row['address_string']
            if not(pd.isna(row['CP'])):
                codigop =  str(row['CP'])
            cadena = address+ "," + codigop
            loc =  obtener_direccion(cadena, "anverso")
            lat = loc.latlng[0]
            long = loc.latlng[1]
                  
        
            if pd.isna(row['CP']): 
                
                
                try:
                    location = str(loc[0])   
                    if re.search("\\d{5}", location).group(0) is not None:
                        cp= re.search("\\d{5}", location).group(0)
                        df.loc[index, 'CP'] = cp
                except:
                    pass
        
            df.loc[index, 'lat'] = lat
            df.loc[index, 'long'] = long
        
    else:
         if pd.isna(row['address_string']):
            lat_punto = str(row['lat']).replace(",", ".")
            long_punto = str(row['long']).replace(",", ".")
            

            df.loc[index, 'lat'] = lat_punto
            df.loc[index, 'long'] = long_punto
       
            list_coordenadas = []
            list_coordenadas.append(lat_punto)
            list_coordenadas.append(long_punto)
            loc=  obtener_direccion(list_coordenadas, "reverso")
            df.loc[index, 'address_string'] = str(loc)
            print(loc)
           
                
            try:
                if pd.isna(row['CP']): 
                    location = str(loc)    

                    if re.search("\\d{5}", location).group(0) is not None:
                        cp= re.search("\\d{5}", location).group(0)
                        df.loc[index, 'CP'] = cp
            except:
                    pass



#obtengo el archivo con las coordenadas de todos los address_strings
df.to_excel(".\\content\\con_coordenadas.xlsx")
