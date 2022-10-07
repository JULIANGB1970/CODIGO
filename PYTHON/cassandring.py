#CON ESTE CODIGO INSERTAMOS DATOS DESDE UN ARCHIVO DE TEXTO A CASSANDRA
#HAY QUE INSTALAR CASSANDRA, EN ESTE CASO Cassandra 2.0.10
#LA VERSION DE PYTHON QUE HAY QUE UTILIZAR ES LA 2.7
#HAY QUE CREAR UNA VARIABLE JAVA_HOME Y AÑADIRLA AL PATH, AL IGUAL QUE CON PYTHON
#EN LA CARPETA BIN DEL DIRECTORIO DE CASSANDRA, EN EL CMD, EJECUTAR CASSANDRA.BAT
#PARA TRABAJAR DESDE LA LINEA DE COMANDOS EJECUTAR EN EL MISMO DIRECTORIO CQLSH


#importamos pandas y la librería de conexión con Cassandra (hay que instalarla con pip)
import pandas as pd 
from cassandra.cluster import Cluster

#leemos el archivo
df = pd.read_csv("VIH_ATTENDER_DIST.csv")

#conectamos con el cluster
cluster = Cluster()
sesion = cluster.connect()
#y empezamos a crear y ejecutar
#aquí elimino el KEYSPACE si existe, para empezar de cero
sesion.execute("DROP KEYSPACE IF EXISTS primero;")
#lo vuelvo a crear
sesion.execute("CREATE KEYSPACE primero with replication =  {'class': 'SimpleStrategy', 'replication_factor':1};")
#empezamos a trabajar con el recien creado keyspace
sesion.execute("use primero;")
#la siguiente instrucción no sería necesaria porque empezamos con el keyspace vacío, pero la pongo a titulo ilustrativo
sesion.execute('drop table if exists VIH ;')
#creo la tabla con sus campos
sesion.execute("CREATE TABLE VIH(id int, county text, STATEABBREVIATION text, dist_SSP float, PRIMARY KEY (id, STATEABBREVIATION)) WITH CLUSTERING ORDER BY (STATEABBREVIATION ASC);")



#itero sobre el dataframe para construir las sentencias sql para cada fila y ejecutarlas 
for row in df.itertuples():
    
    skl = "insert into vih(id, county, STATEABBREVIATION, dist_SSP)  "
    skl = skl + "values(" + str(row[0]) + ",'" + str(row[1])+ "','" + str(row[2]) + "'," +  str(row[3]) + ")"
    sesion.execute(skl)
    skl=""



