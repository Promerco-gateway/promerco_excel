import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# =========================
# 1. Cargar variables de entorno
# =========================
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
PATH_EXCEL = os.getenv("PATH_EXCEL")
TABLE_NAME_ENV = os.getenv("TABLE_NAME")

# =========================
# 2. Parámetros
# =========================
EXCEL_PATH = PATH_EXCEL
SHEET_NAME = 0
TABLE_NAME = TABLE_NAME_ENV
IF_EXISTS = "replace"
CHUNK_SIZE = 1000

# =========================
# 3. Leer Excel
# =========================
print("Leyendo archivo Excel...")

df = pd.read_excel(
    EXCEL_PATH,
    sheet_name=SHEET_NAME,
    engine="openpyxl"
)

print(f"Filas leídas: {len(df)}")

# =========================
# 4. Condición especial
# =========================
if TABLE_NAME == "plan_de_cuentas":
    print("Aplicando formato texto a columna H (plan_de_cuentas)...")
    
    # Columna H = índice 7
    col_h = df.columns[7]
    df[col_h] = df[col_h].astype(str)

# =========================
# 5. Limpieza básica
# =========================
print("Limpiando datos...")

# Normalizar nombres de columnas
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Eliminar filas completamente vacías
df.dropna(how="all", inplace=True)

# Convertir fechas si corresponde
for col in df.select_dtypes(include=["datetime64", "object"]):
    if "fecha" in col:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# Rellenar nulos
df = df.fillna("")

# =========================
# 6. Conexión PostgreSQL
# =========================
print("Conectando a PostgreSQL...")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# =========================
# 7. Insertar datos
# =========================
print("Insertando datos en PostgreSQL...")

df.to_sql(
    name=TABLE_NAME,
    con=engine,
    if_exists=IF_EXISTS,
    index=False,
    chunksize=CHUNK_SIZE,
    method="multi"
)

print("Carga finalizada correctamente")