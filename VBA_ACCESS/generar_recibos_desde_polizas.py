import pyodbc
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random

# ======================================
# CONEXIÓN SQL SERVER
# ======================================
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=WIN-QQJORFBSIIN\\SQLEXPRESS;"
    "DATABASE=SegurosDemo;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

# ======================================
# 1. BORRAR RECIBOS EXISTENTES
# ======================================
print("Eliminando recibos antiguos...")

cursor.execute("DELETE FROM Recibos")
conn.commit()

# ======================================
# 2. LEER PÓLIZAS
# ======================================
cursor.execute("""
    SELECT PolizaID, PrimaAnual, FechaInicio
    FROM Polizas
""")

polizas = cursor.fetchall()

# ======================================
# 3. GENERAR RECIBOS
# ======================================
print("Generando nuevos recibos...")

for p in polizas:

    poliza_id = p.PolizaID
    prima_anual = float(p.PrimaAnual)
    fecha_inicio = p.FechaInicio

    # 12 recibos mensuales
    num_recibos = 12
    importe = round(prima_anual / num_recibos, 2)

    for i in range(num_recibos):

        fecha_emision = fecha_inicio + relativedelta(months=i)
        fecha_vencimiento = fecha_emision + relativedelta(days=30)

        estado = random.choice(["PENDIENTE", "PAGADO"])

        cursor.execute("""
            INSERT INTO Recibos (
                PolizaID,
                FechaEmision,
                FechaVencimiento,
                Importe,
                Estado
            )
            VALUES (?, ?, ?, ?, ?)
        """,
        poliza_id,
        fecha_emision,
        fecha_vencimiento,
        importe,
        estado
        )

# ======================================
# 4. GUARDAR CAMBIOS
# ======================================
conn.commit()
conn.close()

print("Recibos generados correctamente.")