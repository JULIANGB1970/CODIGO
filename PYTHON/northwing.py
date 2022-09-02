
#importo las librerías
#pandas para el tratamiento de datos
import pandas as pd
#numpy para calculos y más
import numpy as np
#gráficos con matplotlin
import matplotlib.pyplot as plt
#para abrir ficheros en el sistema
import os 
#nos servirá para abrir las bases de datos
from sqlalchemy import create_engine
#más gráficos
import seaborn as sns
#librería tratamiento fechas
import datetime






#creamos una conexión con una base de datos en SQL Server
datx = create_engine('mssql+pyodbc://@DESKTOP-3N20FG4/Northwind?driver=ODBC Driver 11 for SQL Server')
#nos conectamos
datx.connect()

#creo una consulta dela base Northwind para tener datos con los que trabajar
skl ="""SELECT  Orders.OrderID, Orders.CustomerID, Orders.EmployeeID, Orders.OrderDate, [Order Details].ProductID, Products.ProductName, [Order Details].UnitPrice, [Order Details].Quantity, Employees.LastName, 
Customers.CompanyName FROM Customers INNER JOIN Orders ON Customers.CustomerID = Orders.CustomerID INNER JOIN [Order Details] ON Orders.OrderID = [Order Details].OrderID INNER JOIN Products ON [Order Details].ProductID = Products.ProductID INNER JOIN
Employees ON Orders.EmployeeID = Employees.EmployeeID"""

#creo un dataframe pandas
pedidos = pd.read_sql(skl, datx)
#aquí aplico un lambda para cambiar aleatoriamente el año y generar datos más diversos
pedidos.OrderDate = pedidos.OrderDate.map(lambda ts: ts.replace(year= np.random.choice([2018, 2019, 2020, 2021])))

#creo un campo calculado en el dataframe
pedidos['importe'] = pedidos['UnitPrice']* pedidos['Quantity']
#creo un campo de año extrayendolo de la fecha
pedidos['anyo'] = pedidos.OrderDate.dt.year

#creo un dataframe conla suma de los importes de los pedidos de cada año
anuales = pd.DataFrame(pedidos.groupby(pedidos.OrderDate.dt.year)['importe'].sum())
#reseteo el index
anuales.reset_index('OrderDate', inplace = True)

#creo un dataframe con las ventas de los 10 productos más vendidos cada año
cantidades = pd.DataFrame(pedidos.groupby(['ProductName', 'anyo'], as_index = False)['importe'].sum().nlargest(10, 'importe'))

#otro dataframe con los pedidos del año 2020
q2021 = pedidos[pedidos.anyo == 2020]
#me muestra los valores únicos y su frecuencia
print(q2021.ProductName.value_counts())

#escribo los datos que he generado a un hoja excel
writer = pd.ExcelWriter(r'data.xlsx', engine = 'openpyxl', mode ='w')
pedidos.to_excel(writer, sheet_name ='npedidos')
anuales.to_excel(writer, sheet_name ='anuales')
q2021.ProductName.value_counts().to_excel(writer, sheet_name ='cantidades')
q2021.ProductName.value_counts().to_excel(writer, sheet_name ='totales')
writer.save()



#abro la hoja
os.startfile(r'data.xlsx')

input("")

#genero un gráfico
fig, axes = plt.subplots(1,1, figsize =(20,15))
#sns.stripplot(ax= axes[0] , x = 'OrderDate', y ='importe', data = anuales)
#sns.stripplot(ax= axes[1] , y = 'ProductName', x ='importe', hue = 'anyo', data = cantidades)
sns.stripplot( y = q2021.ProductName.value_counts().values, x =q2021.ProductName.value_counts().index.tolist(),  data = cantidades)
plt.xticks(rotation=45)
plt.xticks(rotation = 45)
plt.show()


#salgo del programa
exit()

