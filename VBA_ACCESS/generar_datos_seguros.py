import pyodbc
from faker import Faker
import random
from datetime import timedelta

fake = Faker("es_ES")

# =====================================
# CONEXIÓN SQL SERVER
# =====================================
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=WIN-QQJORFBSIIN\\SQLEXPRESS;"
    "DATABASE=SegurosDemo;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

# =====================================
# LIMPIEZA DE TABLAS (ORDEN CORRECTO)
# =====================================
print("Vaciando tablas...")

cursor.execute("DELETE FROM Pagos")
cursor.execute("DELETE FROM Siniestros")
cursor.execute("DELETE FROM Recibos")
cursor.execute("DELETE FROM Polizas")
cursor.execute("DELETE FROM Clientes")
cursor.execute("DELETE FROM UsuariosRoles")
cursor.execute("DELETE FROM Auditoria")

conn.commit()

# =====================================
# LISTAS
# =====================================
clientes = []
polizas = []
siniestros = []

# =====================================
# CLIENTES
# =====================================
print("Generando clientes...")

for _ in range(1000):

    cursor.execute("""
        INSERT INTO Clientes
        (Nombre, Apellidos, DNI, Telefono, Email, Direccion, Provincia)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    fake.first_name(),
    fake.last_name() + " " + fake.last_name(),
    fake.unique.ssn(),
    fake.phone_number(),
    fake.email(),
    fake.address(),
    fake.city()
    )

    conn.commit()

    cursor.execute("SELECT @@IDENTITY")
    clientes.append(int(cursor.fetchone()[0]))

# =====================================
# POLIZAS (SIN DUPLICADOS)
# =====================================
print("Generando pólizas...")

tipos = ["AUTO", "HOGAR", "VIDA", "SALUD"]

poliza_counter = 1

for cliente in clientes:
    for _ in range(random.randint(1, 3)):

        numero_poliza = f"POL{poliza_counter:08d}"
        poliza_counter += 1

        cursor.execute("""
            INSERT INTO Polizas
            (NumeroPoliza, ClienteID, TipoPoliza, FechaInicio, FechaVencimiento, PrimaAnual, Estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        numero_poliza,
        cliente,
        random.choice(tipos),
        fake.date_between("-3y", "today"),
        fake.date_between("today", "+2y"),
        round(random.uniform(200, 1500), 2),
        "ACTIVA"
        )

        conn.commit()

        cursor.execute("SELECT @@IDENTITY")
        polizas.append(int(cursor.fetchone()[0]))

# =====================================
# RECIBOS
# =====================================
print("Generando recibos...")

for poliza in polizas:
    for _ in range(random.randint(1, 4)):

        fecha = fake.date_between("-2y", "today")

        cursor.execute("""
            INSERT INTO Recibos
            (PolizaID, FechaEmision, FechaVencimiento, Importe, Estado)
            VALUES (?, ?, ?, ?, ?)
        """,
        poliza,
        fecha,
        fecha + timedelta(days=30),
        round(random.uniform(50, 400), 2),
        random.choice(["PAGADO", "PENDIENTE"])
        )

        conn.commit()

# =====================================
# SINIESTROS
# =====================================
print("Generando siniestros...")

for poliza in random.sample(polizas, 300):

    if random.random() < 0.25:

        cursor.execute("""
            INSERT INTO Siniestros
            (PolizaID, FechaSiniestro, Tipo, Descripcion, ImporteEstimado, Estado)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        poliza,
        fake.date_between("-2y", "today"),
        random.choice(["ROBO", "ACCIDENTE", "AGUA", "INCENDIO"]),
        fake.text(max_nb_chars=100),
        round(random.uniform(100, 6000), 2),
        "ABIERTO"
        )

        conn.commit()

        cursor.execute("SELECT @@IDENTITY")
        siniestros.append(int(cursor.fetchone()[0]))

# =====================================
# PAGOS
# =====================================
print("Generando pagos...")

for s in siniestros:

    cursor.execute("""
        INSERT INTO Pagos
        (SiniestroID, FechaPago, ImportePagado)
        VALUES (?, ?, ?)
    """,
    s,
    fake.date_between("-1y", "today"),
    round(random.uniform(100, 5000), 2)
    )

conn.commit()

# =====================================
# FIN
# =====================================
print("✔ DATOS GENERADOS CORRECTAMENTE")

cursor.close()
conn.close()