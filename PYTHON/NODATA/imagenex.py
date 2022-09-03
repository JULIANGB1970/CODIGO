from exif import Image
from PIL.ExifTags import TAGS
from PIL import Image
import shutil
import os
from os import path
import pandas as pd 
import time

lista = []


#para utilizar esta función hay que instalar la librería mediante pip install exif
def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    
    ret['ruta'] = str(fn)
    return ret



#indicamos el directorio donde se alojan las imágenes cuya información queremos extraer
origen = "TU DIRECTORIO"


#obtenenemos todos los ficheros en ese directorio
ficheros = os.scandir(origen)

#elegimos lo que nos interesa de ficheros, en este caso las imagenes con formato jpg
imagenes = [fichero.name for fichero in ficheros if fichero.is_file() and fichero.name.endswith('.JPG')]


#hacemos un bucle para extraer la información de cada archivo
for imagen in imagenes:
    #creamos la ruta del archivo
    ruta = path.join(origen, imagen)
    #adjuntamos los datos de la imagen a una lista
    lista.append(get_exif(ruta))


#creamos un dataframe
df = pd.DataFrame(lista)



#la enviamos a una hoja de cálculo
writer = pd.ExcelWriter(os.path.dirname(__file__) + '/../data.xlsx', engine = 'openpyxl', mode ='w')
df.to_excel(writer, sheet_name ='exifz')
writer.save()


#abrimos el archivo
os.startfile(os.path.dirname(__file__) + '/../data.xlsx')
time.sleep(30)
