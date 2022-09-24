Imports System.Data.SqlClient

'Con este programa reduzco el tamaño de las tablas Factonlinesales y Factsales, que tienen inicialmente más de 12 millones y 3 millones de registros. Conservo pedidos para cada una de
'las fechas iniciales de los pedidos originales. El resto de las tablas (Customers, Products...) las dejo como están, porque no llegan ni de lejos al tamaño de las mencionadas y son 
'manejables. Mi objetivo es generar unas nuevas tablas con menos registros (las tablas de sales incluyen el número de pedido y las lineas del pedido en la misma tabla; otra posibilidad hubiera sido
'crear una tabla principal con los números de pedidos y sus fechas y relacionarla con la tabla inicial...) e igualmente representativas. Quiero trabajar con ellas en PowerBi, y aunque hay archivos pbix
'de la base Contoso que se pueden descargar, prefiero tener el control sobre la fuente de datos, y así además poder importar a Access y Excel, para poder repasar cálculos y medidas DAX, cosa muy 
'farragosa en sql server.

'Para  poder probar este código hay que tener instalado SQL Server y recuperar el archivo bak de la base Contoso.






Public Class Form1
    Private Sub Button1_Click(sender As Object, e As EventArgs) Handles Button1.Click
        Using conn As New SqlClient.SqlConnection

            'Creo la conexión a la base en SQL Server, sustituye las Xs por el nombre de tu servidor SQL y las Ys por el nombre de tu base en el servidor
            conn.ConnectionString = "Data Source=XXXXXXX;Initial Catalog=YYYYYY;Integrated Security=True"
            'La abro
            conn.Open()


            Dim BINDX, BINDY As New BindingSource() 'orígenes de datos para los datagrids
            Dim TMPTABLA, TABLA, TABLAX As New DataTable 'creo tablas para manejar los datos 
            Dim skl As New SqlCommand 'un command para ejecutar SQL
            skl.Connection = conn 'configuro la conexión del command
            skl.CommandType = CommandType.Text 'es de tipo text


            Dim FECHA As Date 'creo una variable de fecha
            Dim FECHAX As String 'otra de texto
            Dim ADAPT As New SqlDataAdapter(skl) 'un sqldata adapter


            'aqui empiezo a trabajar con la tabla Factsales 

            skl.CommandText = "select distinct Datekey from factsales" 'obtengo las fechas únicas de la tabla de ventas
            ADAPT.Fill(TMPTABLA) 'lleno la tabla con los datos de la selección



            Try
                skl.CommandText = "drop table tmpx" 'elimino la tabla temporal de trabajo
                skl.ExecuteNonQuery()

            Catch quepasa As Exception

                MsgBox("La tabla temporal no existe, la creo")

            End Try

            skl.CommandText = "select top 5 salesquantity, saleskey, DateKey into tmpx from  factsales" 'creo una tabla tamporal
            skl.ExecuteNonQuery()
            skl.CommandText = "delete from tmpx" 'borro los datos iniciales con los que he creado la tabla
            skl.ExecuteNonQuery()



            For Each fila As DataRow In TMPTABLA.Rows
                'hago un loop para introducir en la tabla temporal 5 registros para cada fecha
                FECHA = fila(0)
                FECHAX = Trim(Str(FECHA.Year)) & "/" & Trim(Str(FECHA.Month)) & "/" & Trim(Str(FECHA.Day))
                skl.CommandText = "SET IDENTITY_INSERT tmpx ON  insert into tmpx([salesquantity], [saleskey], [datekey])  select top 5 salesquantity, saleskey, DateKey from factsales where factsales.DateKey = '" & FECHAX & "'"
                skl.ExecuteNonQuery()

            Next



            'elimino la tabla que va a recoger los registros seleccionados, si se había creado en ejecuciones anteriores, para volverla a crear de nuevo
            'esto asegura que trabajamos siempre con datos limpios cada vez que ejecutamos el código
            Try
                skl.CommandText = "drop table XFACTSALES"
                skl.ExecuteNonQuery()
            Catch quepasa As Exception
                MsgBox("La tabla definitiva no existe, la creo")


            End Try

            'introduzco los datos definitivos en la tabla final que quiero crear. 
            skl.CommandText = "Select FactSales.* into  XFACTSALES FROM FACTSALES INNER JOIN TMPX On FACTSALES.SalesKey= TMPX.SALESKEY"
            skl.ExecuteNonQuery()


            'genero una consulta y lleno el datagrid
            skl.CommandText = "select *  from XFACTSALES order by datekey asc"
            ADAPT.Fill(TABLA)
            datagridx.DataSource = Nothing
            BINDX.DataSource = TABLA
            datagridx.DataSource = BINDX
            datagridx.Refresh()



            '////////////////////////////////////////////////////////////////////

            'utilizo el mismo procedimiento para trabajar con la tabla factonlinesales, que tiene más de 12 millones de registros

            'empiezo eliminando lineas de los pedidos porque no necesito tantas, me quedo con tres por pedido como mucho;
            'aqui la tabla factonlinesales ya no va a ser la original; para trabajar sin tocarla, se podría haber duplicado
            'si después de ejecutado el código, se quieren volver a utilizar los registros iniciales hay que recuperar la base de datos
            skl.CommandText = "DELETE FROM FactOnlineSales WHERE SalesOrderLineNumber >3"
            skl.CommandTimeout = 1000000 'tengo que aumentar el tiempo de ejecución, en total el código se ejecuta en cinco minutos más o menos

            skl.ExecuteNonQuery()

            'selecciono valores únicos de fecha
            skl.CommandText = "select distinct Datekey from factonlinesales"
            TMPTABLA.Clear()
            ADAPT.Fill(TMPTABLA)

            'elimino tabla y vuelvo a crear
            Try
                skl.CommandText = "drop table tmpx"
                skl.ExecuteNonQuery()

            Catch quepasa As Exception

                MsgBox("La tabla temporal no existe, la creo")

            End Try


            skl.CommandText = "select top 5 salesquantity, onlinesaleskey, DateKey into tmpx from  factonlinesales"
            skl.ExecuteNonQuery()
            skl.CommandText = "delete from tmpx"
            skl.ExecuteNonQuery()


            'hago el loop idéntico al anterior con la tabla Factonlinesales
            For Each fila As DataRow In TMPTABLA.Rows

                FECHA = fila(0)
                FECHAX = Trim(Str(FECHA.Year)) & "/" & Trim(Str(FECHA.Month)) & "/" & Trim(Str(FECHA.Day))

                skl.CommandText = "SET IDENTITY_INSERT tmpx ON insert into tmpx([salesquantity], [onlinesaleskey], [datekey])  select top 10 salesquantity, onlinesaleskey, DateKey from factonlinesales where factonlinesales.DateKey = '" & FECHAX & "'"
                skl.ExecuteNonQuery()

            Next



            'eliminio y creo de nuevo la tabla definitiva de factonlinesales, reducida
            Try
                skl.CommandText = "drop table XFACTONLINESALES"
                skl.ExecuteNonQuery()
            Catch quepasa As Exception
                MsgBox("La tabla definitiva no existe, la creo")

            End Try

            skl.CommandText = "Select Factonlinesales.* into  XFACTONLINESALES FROM FACTONLINESALEs INNER JOIN TMPX On FACTONLINESALEs.onlineSalesKey= TMPX.onlineSALESKEY"
            skl.ExecuteNonQuery()



            'ejecuto una selección con los registros finales y lo meto en un datagrid 

            skl.CommandText = "select *  from XFACTONLINESALES order by datekey asc"

            ADAPT.Fill(TABLAX)

            BINDY.DataSource = TABLAX
            datagridy.DataSource = Nothing
            datagridy.DataSource = BINDY
            datagridy.Refresh()










        End Using


    End Sub

    Private Sub Form1_Load(sender As Object, e As EventArgs) Handles MyBase.Load

    End Sub

    Private Sub Form1_KeyPress(sender As Object, e As KeyPressEventArgs) Handles Me.KeyPress

        If Asc(e.KeyChar) = 27 Then
            Me.Dispose()
        End If


    End Sub
End Class
