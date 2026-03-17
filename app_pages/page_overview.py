# ============================================
# Page Overview
# ============================================

# Importar librerías 
import streamlit as st
from PIL import Image

# Importar rutas de configuración
from common.config import (
    ASSETSIMG
)

# Importar funciones de datos y filtros
from controllers.db_controller import load_stats_players_fbref
from common.filters import apply_player_filters

# Función que da cómo resultado la página Overview
def page_overview():

    # Se crean 3 columnas para centrar la imagen
    overview_imgcol1, overview_imgcol2, overview_imgcol3 = st.columns([3, 2, 3])

    with overview_imgcol2:

        # Se carga una imagen desde la carpeta assets
        overview_img_filter = Image.open(ASSETSIMG / "Freepick Filter.png")

        # Se muestra la imagen en Streamlit
        st.image(overview_img_filter, width=120)

    # Título de la página
    st.header("Player Visualization and Filtering")
    
    # Cargar datos desde la base de datos
    overview_df_players = load_stats_players_fbref()

    # Diccionario con los valores iniciales de los filtros
    overview_defaults = {
        "overview_age_filter": "All",
        "overview_pos_filter": "All",
        "overview_team_filter": "All",
        "overview_league_filter": "All",
        "overview_minutes_filter": 0,
        "overview_num_players_filter": 100,
        "overview_do_reset": False,
    }

    # Si alguna variable no existe en session_state se crea
    for key, value in overview_defaults.items():
        st.session_state.setdefault(key, value)

    # Si el botón de reset fue presionado
    if st.session_state["overview_do_reset"]:

        # Restaurar todos los filtros a valores iniciales
        st.session_state["overview_age_filter"] = "All"
        st.session_state["overview_pos_filter"] = "All"
        st.session_state["overview_team_filter"] = "All"
        st.session_state["overview_league_filter"] = "All"
        st.session_state["overview_minutes_filter"] = 0
        st.session_state["overview_num_players_filter"] = 100

        # Desactivar flag de reset
        st.session_state["overview_do_reset"] = False

        # Recargar la app
        st.rerun()

    # Layout de la página
    overview_col1, overview_col2, overview_col3, overview_col4, overview_col5, overview_col6 = st.columns([2,2,2,2,2,2])

    # Aplicar filtros reutilizables
    overview_filtered_df = apply_player_filters(
        overview_df_players,
        overview_col1,
        overview_col2,
        overview_col3,
        overview_col4,
        overview_col5,
        prefix="overview"
    )

    # Slider para limitar número de jugadores
    with overview_col6:

        overview_num_players = st.slider(
            "N° Players",
            0,
            100,
            key="overview_num_players_filter"  # Streamlit usará el valor de session_state automáticamente
        )

    # Limitar número de jugadores mostrados
    overview_filtered_df = overview_filtered_df.head(overview_num_players)

    # Línea visual separadora
    st.divider()

    # Dataframe interactivo de Streamlit
    st.dataframe(
        overview_filtered_df,
        hide_index=True,

        # Configuración de columnas
        column_config={

            # Fijar columnas a la izquierda para mejor visualización
            "Id_player": st.column_config.Column(pinned="left"),
            "Player": st.column_config.Column(pinned="left"),
        }
    )

    # Botón para resetear filtros
    if st.button("🔄 Reset filters"):

        # Activar flag de reset
        st.session_state["overview_do_reset"] = True

        # Recargar la página
        st.rerun()