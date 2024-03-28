from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.files.file import File 
import os
import pandas as pd

from sqlalchemy import create_engine
import time
import csv
from io import StringIO
import psycopg2
from psycopg2.extras import execute_values






user ='*****'
password= '*******'




#en esta parte del código creo el contexto para trabajar con Sharepoint
auth = AuthenticationContext('https://universidaddealcala.sharepoint.com/sites/ASISTENCIA/')
auth.acquire_token_for_user(user, password)
ctx = ClientContext('https://universidaddealcala.sharepoint.com/sites/ASISTENCIA/', auth)
web = ctx.web
ctx.load(web)
ctx.execute_query()
print('Connected to SharePoint: ',web.properties['Title'])


folder_in_sharepoint = '/sites/ASISTENCIA/Documentos compartidos/' 



#esta función me devuelve los ficheros contenidos en la carpeta documentos compartidos
def folder_details(ctx, folder_in_sharepoint):
  folder = ctx.web.get_folder_by_server_relative_url(folder_in_sharepoint)
  fold_names = []
  sub_folders = folder.files 
  ctx.load(sub_folders)
  ctx.execute_query()
  for s_folder in sub_folders:
    fold_names.append(s_folder.properties["Name"])
  print(fold_names)
  return fold_names


folder_details(ctx, folder_in_sharepoint)

#esta instrucción elimina una carpeta existente
#ctx.web.get_folder_by_server_relative_path("/sites/ASISTENCIA/Documentos compartidos/ARCHIVOS").delete_object().execute_query()


#leo este csv con 2.075.259 registros
df = pd.read_csv("household_power_consumption.csv", sep =";", low_memory=False)
#convierto la columna a datetime
df['Date'] = pd.to_datetime(df['Date'])
df['Year']= df['Date'].dt.year
print(df.head())
print(len(df))

#obtengo lsos años regsitrados en el csv
anyos = df.Year.unique()
print(anyos)


#creo el motodr de base de datos con el que insertar los datos posteriormente
conn=psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='Candel@051211',
    host='localhost',
    port='5432'
) 


#establezco el punto de inicio para medir el tiempo de inserción en la base de datos
start_time = time.time() 

for anyo in anyos:

    if anyo == 2009:
        print(anyo)    
        grouped = df.groupby(df.Year)

        #creo un dataframe para cada año
        df_year=  grouped.get_group(anyo)
        #lo guardo  en un csv
        df_year.to_csv(str(anyo) + ".csv")

        #introduzco los datos en postgre
        sio = StringIO()
        df_year.to_csv(sio, index=None, header=None)
        sio.seek(0)
        with conn.cursor() as c:
            c.copy_expert(
            sql="""
                COPY CONSUMOS (
            Date,
            Time,
            Global_active_power,
            Global_reactive_power,
            Voltage,
            Global_intensity,
            Sub_metering_1,
            Sub_metering_2,
            Sub_metering_3,
            yearx
        ) FROM STDIN WITH CSV""",
        file=sio)
        conn.commit()
    else:
        pass
  

#obtengo la duración del proceso
end_time = time.time() 
total_time = end_time - start_time 
print(f"Tiempo de inserción: {total_time} segundos") 



#aqui simplemenete por trabajar con Sharepoint subo los csvs generados antriormente

anyos=[2006,2007,2008,2009,2010]

for anyo in anyos:

    with open(str(anyo)+ ".csv","rb") as content_file:
        file_content = content_file.read()

        remotepath = "/sites/ASISTENCIA/Documentos compartidos/"+ str(anyo)+ ".csv"
        dir, name = os.path.split(remotepath)
        file = ctx.web.get_folder_by_server_relative_url(dir).upload_file(name, file_content).execute_query()



#los vuelvo a descargar con otro nombre
for anyo in anyos:

        file_url = "/sites/ASISTENCIA/Documentos compartidos/"+ str(anyo)+ ".csv" 
        source_file = ctx.web.get_file_by_server_relative_path(file_url)  
        local_file_name = "downloaded_"+ str(anyo) + ".csv"
  
        with open(local_file_name, "wb") as local_file:  
             source_file.download_session(local_file).execute_query()  




#finalmente los elimino de Sharepoint
for anyo in anyos:

    file_rel_url = "/sites/ASISTENCIA/Documentos compartidos/"+ str(anyo)+ ".csv"
    file_to_delete = ctx.web.get_file_by_server_relative_url(file_rel_url)  
    file_to_delete.delete_object()
    ctx.execute_query()






