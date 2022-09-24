En el código de este formulario de Microsoft Visual Studio 2019, reduzco el tamaño de 
las tablas principales Factonlinesales y FactonlineSales ( de 12 millones y más de 3 millones de registros cada una).
La idea es conservar todas las fechas existentes en esas tablas pero eliminar lineas de cada pedido único para poder 
trabajar con ellas posteriormente en Power BI. Hay archivos pbix de esta base para descargar, pero con este código
y/o alguna modificación se pueden tratar los datos a demanda y los hacen más manejables para la máquina y también para
el usuario que puede analizarlas y calcularlas en aplicaciones más amigables que SQL Server, como Access y Excel.