# ============================================
# Page League Requests 
# ============================================

# Importar librerías
import streamlit as st
import pandas as pd
import os
from PIL import Image

# Importar rutas de configuración
from common.config import (
    ASSETSIMG, DATA_DIR
)

# Función que da como resultado la página Message
def page_league_requests_admin():

    # Seguridad: solo admin
    if not st.session_state.get("is_admin"):
        st.error("Access denied. Admin only.")
        st.stop()
        
    # Se crean 3 columnas para centrar la imagen
    message_imgcol1, message_imgcol2, message_imgcol3 = st.columns([3,2,3])
    
    with message_imgcol2:
    
        # Se carga una imagen desde la carpeta assets
        header_img = Image.open(ASSETSIMG / "Freepick Message.png")
    
        # Se muestra la imagen en Streamlit
        st.image(header_img, width=120)

    # Título de la página
    st.header("League Requests Management")
    
    st.caption("Review and manage league requests from users")
    
    st.markdown("---")

    # Definir ruta del archivo Excel donde se almacenan los mensajes
    MESSAGE_FILE = DATA_DIR / "message_from_users.xlsx"

    # Función auxiliar para cargar solicitudes de ligas desde el Excel
    def load_requests():
        
        # Columnas esperadas en el DataFrame
        columns = ["User", "League", "Priority", "Message", "Date", "Status"]
        
        # Si el archivo no existe, devolver un DataFrame vacío con las columnas definidas
        if not os.path.exists(MESSAGE_FILE):
            return pd.DataFrame(columns=columns)
        
        # Cargar las solicitudes existentes desde Excel
        df = pd.read_excel(MESSAGE_FILE)

        # Asegurar que todas las columnas esperadas existen
        for col in columns:
            if col not in df.columns:
                df[col] = ""

        # Asegurar que Status es una columna de texto
        df["Status"] = df["Status"].fillna("").astype("string")

        # Poner Pending donde Status esté vacío
        df.loc[df["Status"] == "", "Status"] = "Pending"
        
        # Devolver el DataFrame cargado
        return df

    # Función auxiliar para guardar solicitudes
    def save_requests(df):
        
        # Guardar DataFrame en Excel, sobrescribiendo el archivo
        with pd.ExcelWriter(MESSAGE_FILE, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, index=False)
        
    # Cargar todas las solicitudes al iniciar la página
    df_requests = load_requests()
    
    # Si no hay solicitudes, mostrar mensaje informativo y terminar la ejecución
    if df_requests.empty:
        st.info("No league requests available")
        return

    # Mostrar cada solicitud en la interfaz
    for i, row in df_requests.iterrows():

        # Layout de la página
        col1, col2, col3, col4, col5 = st.columns([3,3,2,2,2])

        # Columna 1: Usuario que envió la solicitud
        with col1:
            st.markdown(f"**👤 {row['User']}**")
        
        # Columna 2: Liga solicitada
        with col2:
            st.markdown(f"**🏆 {row['League']}**")
        
        # Columna 3: Prioridad de la solicitud
        with col3:
            priority_icon = {"Low":"🟢","Medium":"🟡","High":"🔴"}.get(row["Priority"], "⚪")
            st.markdown(f"{priority_icon} **{row['Priority']}**")
        
        # Columna 4: Fecha de la solicitud
        with col4:
            st.markdown(f"📅 {row['Date']}")
        
        # Columna 5: Estado de la solicitud
        with col5:
            status_icon = "✅" if row["Status"]=="Approved" else "⏳"
            st.markdown(f"{status_icon} **{row['Status']}**")

        # Segunda fila: mensaje completo
        msg_col1, msg_col2, msg_col3 = st.columns([8,2,2])

        # Columna 1: Mensaje completo 
        with msg_col1:
            st.markdown(f"💬 **Message:** {row['Message']}")

        # Columna 2: Botón de aprobación
        with msg_col2:
            
            # Solo permitir aprobar si no está ya aprobado
            if row["Status"] != "Approved":
                
                # Botón para aprobar la solicitud
                if st.button("Approve", key=f"approve_{i}"):
                    
                    # Cambiar estado a "Approved"
                    df_requests.loc[i,"Status"] = "Approved"
                    
                    # Guardar cambios en el Excel
                    save_requests(df_requests)
                    
                    # Mensaje de éxito
                    st.success("League request approved")
                    
                    # Recargar la página para actualizar la visualización
                    st.rerun()
                    
            else:
                # Si ya está aprobado, mostrar botón deshabilitado
                st.button("Approved", disabled=True, key=f"done_{i}")

        # Columna 3: Botón para eliminar solicitud
        with msg_col3:
            
            # Botón para eliminar solicitud
            if st.button("🗑️", key=f"delete_req_{i}"):
                
                # Eliminar la fila correspondiente del DataFrame
                df_updated = df_requests.drop(i).reset_index(drop=True)
                
                # Guardar cambios en el Excel
                save_requests(df_updated)
                
                # Mensaje de advertencia al administrador
                st.warning("Request deleted")
                
                # Recargar la página para actualizar la visualización
                st.rerun()

        # Línea divisoria visual entre solicitudes
        st.divider()