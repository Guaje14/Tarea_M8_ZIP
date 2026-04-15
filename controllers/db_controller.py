# ============================================
# Controllers -> db_controller
# ============================================

# Importar librerías 
import sqlite3
import pandas as pd
import streamlit as st

# Importar rutas de configuración
from common.config import (
    DB_PATH
)

# Función para crear conexión a la base de datos SQLite
def get_connection():
    """Retorna la conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    return conn


@st.cache_data(ttl=2_592_000)  # 30 días aprox
# Función para leer y cargar los datos de Fbref
def load_stats_players_fbref():

    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)

    # Leer toda la tabla de estadísticas de jugadores
    df = pd.read_sql_query("SELECT * FROM stats_players_fbref", conn)

    # Cerrar conexión a la base de datos
    conn.close()

    # Columnas que deben mantenerse como texto
    text_cols = ["Player", "stats_Nation", "stats_Pos", "stats_Squad", "stats_Comp", "league"]

    # Obtener todas las columnas excepto las de texto
    numeric_cols = df.columns.difference(text_cols)

    # Convertir columnas numéricas automáticamente
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    return df  