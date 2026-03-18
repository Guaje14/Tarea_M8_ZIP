# ============================================
# Controllers -> logs_export_csv
# ============================================

# Importar librerías 
from datetime import datetime
import streamlit as st
import pandas as pd
from pathlib import Path

# Importar rutas de configuración
from common.config import (
    LOG_FILE
)

# Función para generar un registro de la descarga
def build_download_log(page_name: str, prefix: str, extra_data: dict = None):
    
    # Construcción del log base
    log_data = {
    
        # Usuario (si no existe en session → 'anonymous')
        "user": st.session_state.get("user", "anonymous"),

        # Timestamp del momento de la descarga
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        # Página desde donde se realiza la acción
        "page": page_name,

        # Filtros dinámicos (dependen del prefijo)
        "age_filter": st.session_state.get(f"{prefix}_age_filter"),
        "pos_filter": st.session_state.get(f"{prefix}_pos_filter"),
        "team_filter": st.session_state.get(f"{prefix}_team_filter"),
        "league_filter": st.session_state.get(f"{prefix}_league_filter"),
        "minutes_filter": st.session_state.get(f"{prefix}_minutes_filter"),
        "num_players": st.session_state.get(f"{prefix}_num_players_filter"),
    }

    # Añadir información extra si existe (ej: estadísticas, ranking, etc.)
    if extra_data:
        log_data.update(extra_data)

    return log_data
    
# Función para guardar registros de logs en un archivo Excel
def save_log_to_excel(log_data: dict):

    # Convertir el log en un DataFrame de una sola fila
    new_row = pd.DataFrame([log_data])

    # Si el archivo existe → añadir datos
    if LOG_FILE.exists():
        existing_df = pd.read_excel(LOG_FILE)
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    else:
        # Si no existe → crear nuevo archivo
        updated_df = new_row

    # Guardar en Excel
    updated_df.to_excel(LOG_FILE, index=False)

# Función para generar y registrar un evento de descarga
def log_download_event(page_name: str, prefix: str, extra_data: dict = None):
    
    # Generar log con toda la información
    log_data = build_download_log(page_name, prefix, extra_data)

    # Guardar en Excel
    save_log_to_excel(log_data)

    # Mostrar en consola (útil para debugging)
    print("LOG EXPORT:", log_data)