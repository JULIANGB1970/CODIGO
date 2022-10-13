import pandas as pd
from pymongo import MongoClient
import json




#Aquí creamos la conexión con una base de datos Mongo local; la instalación de mongo es gratuita, hay que tener un directorio /data/db/ colgando de C:>
#y ejecutar los procesos mongod y mongos de la carpeta bin de la instalación de mongo en archivos de programa
myclient =MongoClient("mongodb://localhost:27017/")


#aquí leemos los datos de un archivo csv en un dataframe
df = pd.read_csv("\DATA\VIH_ATTENDER_DIST.csv")


#con esta instrucción genero un diccionario
diccionario = df.to_dict("records")


#creo una base de datos nueva en mongo
mibase = myclient["vih"]

#creo una tabala en la base de datos nueva
mitabla = mibase["datos"]

#inserto el diccionario tal cual en mongo.
mitabla.insert_many(diccionario)












