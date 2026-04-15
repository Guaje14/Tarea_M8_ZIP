# ============================================
# Controllers -> user_controller
# ============================================

# Importar librerías
import streamlit as st
import bcrypt
from sqlalchemy import text
from models.user import User

# Función para obtener conexión a la base de datos
def get_conn():
    return st.connection("users_db", type="sql")

# Función para generar hash de contraseña
def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

# Función para verificar contraseña frente al hash
def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )

# Función para cargar todos los usuarios desde la base de datos
def load_users():

    # Obtener conexión
    conn = get_conn()

    # Ejecutar consulta de usuarios
    with conn.session as session:
        rows = session.execute(
            text("""
                SELECT username, password_hash, role
                FROM users
                ORDER BY username
            """)
        ).fetchall()

    # Crear lista de objetos User
    users = []

    # Recorrer resultados y construir usuarios
    for row in rows:
        username, password_hash, role = row
        users.append(
            User(
                username=username,
                password=password_hash,
                role=role
            )
        )

    return users

# Función para crear un nuevo usuario
def create_user(username, password, role="viewer"):

    # Obtener conexión
    conn = get_conn()

    # Generar hash de la contraseña
    password_hash = hash_password(password)

    # Comprobar si el usuario ya existe
    with conn.session as session:
        exists = session.execute(
            text("""
                SELECT 1
                FROM users
                WHERE username = :username
            """),
            {"username": username}
        ).fetchone()

        if exists:
            return False, "The user already exists"

        # Insertar nuevo usuario
        session.execute(
            text("""
                INSERT INTO users (username, password_hash, role)
                VALUES (:username, :password_hash, :role)
            """),
            {
                "username": username,
                "password_hash": password_hash,
                "role": role
            }
        )
        session.commit()

    return True, f"User '{username}' created successfully"

# Función para actualizar el rol de un usuario
def update_user(username, role=None):

    # Salir si no hay cambios
    if role is None:
        return

    # Obtener conexión
    conn = get_conn()

    # Ejecutar actualización
    with conn.session as session:
        session.execute(
            text("""
                UPDATE users
                SET role = :role
                WHERE username = :username
            """),
            {
                "username": username,
                "role": role
            }
        )
        session.commit()

# Función para eliminar un usuario
def delete_user(username):

    # Obtener conexión
    conn = get_conn()

    # Ejecutar borrado
    with conn.session as session:
        session.execute(
            text("""
                DELETE FROM users
                WHERE username = :username
            """),
            {"username": username}
        )
        session.commit()

# Función para autenticar usuario en el login
def authenticate_user(username, password):

    # Obtener conexión
    conn = get_conn()

    # Buscar usuario por nombre
    with conn.session as session:
        row = session.execute(
            text("""
                SELECT username, password_hash, role
                FROM users
                WHERE username = :username
            """),
            {"username": username}
        ).fetchone()

    # Devolver None si no existe
    if not row:
        return None

    # Extraer datos del usuario
    username_db, password_hash, role = row

    # Verificar contraseña
    if verify_password(password, password_hash):
        return User(
            username=username_db,
            password=password_hash,
            role=role
        )

    return None

# Función para registrar accesos
def log_access(username, role="viewer"):

    # Obtener conexión
    conn = get_conn()

    # Insertar registro de acceso
    with conn.session as session:
        session.execute(
            text("""
                INSERT INTO access_log (username, role)
                VALUES (:username, :role)
            """),
            {
                "username": username,
                "role": role
            }
        )
        session.commit()