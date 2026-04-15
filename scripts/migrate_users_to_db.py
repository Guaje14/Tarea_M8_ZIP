# ============================================
# Scripts -> migrate_users_to_db
# ============================================

# Importar librerías
import pandas as pd
import bcrypt
import tomllib
from pathlib import Path
from sqlalchemy import create_engine, text

# Configuración de paths y archivos
BASE_DIR = Path(__file__).resolve().parents[1]
SECRETS_FILE = BASE_DIR / ".streamlit" / "secrets.toml"
USERS_XLSX = BASE_DIR / "data" / "users.xlsx"

# Leer la URL de conexión desde secrets.toml
with open(SECRETS_FILE, "rb") as f:
    secrets = tomllib.load(f)

db_url = secrets["connections"]["users_db"]["url"]

# Crear engine SQLAlchemy
engine = create_engine(db_url)

# Leer usuarios desde el Excel
df = pd.read_excel(USERS_XLSX)

# Limpiar nombres de columnas
df.columns = [str(col).strip().lower() for col in df.columns]

# Validar columnas necesarias
required_cols = {"user", "password", "role"}
missing = required_cols - set(df.columns)

if missing:
    raise ValueError(f"Faltan columnas en users.xlsx: {missing}")

# SQL de creación de tablas
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer'
);
"""

create_access_log_table = """
CREATE TABLE IF NOT EXISTS access_log (
    id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    role TEXT,
    hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

# SQL de inserción/actualización
insert_user_sql = """
INSERT INTO users (username, password_hash, role)
VALUES (:username, :password_hash, :role)
ON CONFLICT (username)
DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role;
"""

valid_roles = {"admin", "viewer"}

# Ejecutar migración
with engine.begin() as conn:
    conn.execute(text(create_users_table))
    conn.execute(text(create_access_log_table))

    for _, row in df.iterrows():
        if pd.isna(row["user"]) or pd.isna(row["password"]):
            raise ValueError("Hay usuarios con nombre o contraseña vacíos en users.xlsx")

        username = str(row["user"]).strip()
        raw_password = str(row["password"]).strip()
        role = str(row["role"]).strip().lower() if pd.notna(row["role"]) else "viewer"

        if not username or not raw_password:
            raise ValueError("Username o password vacíos detectados en users.xlsx")

        if role not in valid_roles:
            raise ValueError(f"Rol no válido para {username}: {role}")

        password_hash = bcrypt.hashpw(
            raw_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        conn.execute(
            text(insert_user_sql),
            {
                "username": username,
                "password_hash": password_hash,
                "role": role
            }
        )

print("Migración completada correctamente.")