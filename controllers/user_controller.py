# ============================================
# Controllers -> user_controller
# ============================================

# Importar librerías 
import pandas as pd
from datetime import datetime

# Importar el modelo de usuario
from models.user import User

# Importar rutas de configuración
from common.config import (
    ACCESS_LOG, USERS_FILE
)

# Función para cargar los usuarios desde el Excel
def load_users():
    
    # Leer archivo Excel de usuarios
    df = pd.read_excel(USERS_FILE)

    # Convertir cada fila en un objeto User
    users = []
    
    for _, row in df.iterrows():
        users.append(
            User(
                username=row["user"],           # Columna usuario
                password=row["password"],       # Columna contraseña
                role=row.get("role", "viewer")  # Rol por defecto si no existe
            )
        )

    return users

# Función para guardar los nuevos usuarios al Excel
def save_users(users):
    
    # Convertir objetos User a diccionarios (estructura tabla)
    data = [{
        "user": u.username,
        "password": u.password,
        "role": u.role
    } for u in users]

    # Crear DataFrame
    df = pd.DataFrame(data)

    # Guardar en Excel
    df.to_excel(USERS_FILE, index=False)

# Función para verificar si un usuario existe y si la contraseña es correcta
def authenticate_user(username, password):
    
    # Cargar usuarios
    users = load_users()

    # Buscar coincidencia
    for user in users:
        if user.username == username and user.password == password:
            return user  # Usuario válido

    return None  # No encontrado

# Registrar acceso de un usuario
def log_access(username):

    # Obtener fecha y hora actual
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Buscar el usuario en la lista
    user = None
    users = load_users()

    for u in users:
        if u.username == username:
            user = u
            break

    # Si existe el usuario → usar su rol
    rol = user.role if user else "viewer"

    # Crear nuevo registro de acceso
    nuevo = pd.DataFrame(
        [[username, rol, hora]],
        columns=["Usuario", "Rol", "Hora"]
    )

    try:
        # Leer archivo existente
        df = pd.read_excel(ACCESS_LOG)

        # Añadir nuevo registro
        df = pd.concat([df, nuevo], ignore_index=True)

    except Exception:
        # Si el archivo no existe, crear uno nuevo
        df = nuevo

    # Guardar archivo actualizado
    df.to_excel(ACCESS_LOG, index=False)