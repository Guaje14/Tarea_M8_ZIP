# ============================================
# Page Admin
# ============================================

# Importar librerías 
import streamlit as st
import pandas as pd
from PIL import Image

# Importar el modelo de usuario
from models.user import User

# Importar rutas de configuración
from common.config import (
    ASSETSIMG
)

# Importar funciones de usuarios
from controllers.user_controller import load_users, save_users
    
# Función que da como resultado la página Admin
def page_admin():
    
    # Seguridad: solo admin
    user = st.session_state.get("user")
    if not user or not user.is_admin():
        st.error("Access denied. Admin only.")
        st.stop()
    
    # Se crean 3 columnas para centrar la imagen
    admin_imgcol1, admin_imgcol2, admin_imgcol3 = st.columns([3, 2, 3])

    with admin_imgcol2:
        
        # Se carga una imagen desde la carpeta assets
        admin_img_header = Image.open(ASSETSIMG / "Freepick Admin.png")
        
        # Se muestra la imagen en Streamlit
        st.image(admin_img_header, width=120)
    
    # Layout de la página
    admin_col1, admin_col2, admin_col3 = st.columns([1.5, 2.5, 2.5])  
    
    # Cargar Usuarios  
    admin_users = load_users()

    # Formulario para insertar un nuevo usuario
    with admin_col2:
        st.header("Create / Manage Users")        
        
        # Crear nuevo usuario
        new_user = st.text_input("New User", placeholder="Insert new User", key="new_user")
        new_pass = st.text_input("New Password", placeholder="Insert new Password", type="password", key="new_pass")
        new_role = st.selectbox("Role", ["viewer", "admin"], key="new_role")
        
        # Botón para crear nuevo usuario
        if st.button("Create New User"):
            
            if not new_user or not new_pass:
                st.error("User and Password required")
                
            elif any(u.username == new_user for u in admin_users):
                st.warning("The user already exists")
            
            else:
                # Crear objeto User
                user_obj = User(
                    username=new_user,
                    password=new_pass,
                    role=new_role
                )

                # Añadir y guardar
                admin_users.append(user_obj)
                save_users(admin_users)
                
                
                st.success(f"User '{new_user}' created successfully")
                st.rerun()

        st.markdown("---")
        st.subheader("Users Created:")
        st.write("Logged user:", user.username)

        # Recorrer cada usuario del DataFrame
        for i, u in enumerate(admin_users):

            # Crear layout de 4 columnas para organizar la información del usuario
            admin_c1, admin_c2, admin_c3, admin_c4 = st.columns([4,4,1,2])

            # Cargar Usuario 
            with admin_c1:
                
                # Elegir icono según el rol del usuario
                role_icon = "🛠️" if u.role == "admin" else "👁️"
                
                # Mostrar nombre de usuario y rol
                st.markdown(
                    f"""
                    **👤 {u.username}**\n  
                    {role_icon} **{u.role}**
                    """
                )

            # Cambiar ROLE 
            with admin_c2:
                
                # Selector desplegable para cambiar el rol
                new_role_user = st.selectbox(
                    "Role",
                    ["viewer", "admin"],
                    index=["viewer","admin"].index(u.role),
                    key=f"role_{i}"
                )

                # Si el rol seleccionado es distinto al actual
                if new_role_user != u.role:

                    # Actualizar el rol en el DataFrame
                    admin_users[i, "role"] = new_role_user

                    # Guardar cambios en el archivo Excel
                    save_users(admin_users)

                    # Mostrar confirmación al usuario
                    st.success(f"Role updated for {u.username}")

                    # Recargar la app para reflejar los cambios
                    st.rerun()

            # Eliminar Usuario 
            with admin_c4:
                
                # Evitar que el usuario logueado pueda eliminar su propia cuenta
                if u.username == user.username:

                    # Mostrar botón bloqueado (sin interacción)
                    st.button("🛡️", disabled=True, key=f"lock_{i}")

                else:

                    # Botón para eliminar usuario
                    if st.button("🗑️", key=f"delete_user_{i}"):

                        # Eliminar usuario del DataFrame
                        admin_users.pop(i)

                        # Guardar cambios en el Excel
                        save_users(admin_users)

                        # Mostrar mensaje de confirmación
                        st.warning(f"User {u.username} deleted")

                        # Recargar la app para actualizar la lista
                        st.rerun()

            # Línea divisoria visual entre usuarios
            st.divider()