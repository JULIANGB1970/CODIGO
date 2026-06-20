import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=WIN-QQJORFBSIIN\\SQLEXPRESS;"
    "DATABASE=SegurosDemo;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM Clientes")
print(cursor.fetchone()[0])