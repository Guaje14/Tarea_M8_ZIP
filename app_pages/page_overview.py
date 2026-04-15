# ============================================
# Page Overview
# ============================================

# Importar librerías
import streamlit as st
from PIL import Image
import io

# Importar rutas de configuración
from common.config import (
    ASSETSIMG
)

# Importar funciones de datos y filtros
from controllers.db_controller import load_stats_players_fbref
from common.filters import apply_player_filters_overview_rk
from controllers.logs_export_csv import log_download_event

# Función que da cómo resultado la página Overview
def page_overview():

    # Crear 3 columnas para centrar la imagen
    overview_imgcol1, overview_imgcol2, overview_imgcol3 = st.columns([3, 2, 3])

    with overview_imgcol2:

        # Cargar imagen desde la carpeta assets
        overview_img_filter = Image.open(ASSETSIMG / "Freepick Filter.png")

        # Mostrar imagen en Streamlit
        st.image(overview_img_filter, width=120)

    # Título de la página
    st.header("Player Visualization and Filtering")

    # Cargar datos desde la base de datos
    overview_df_players = load_stats_players_fbref()

    # Definir valores por defecto de los filtros
    overview_defaults = {
        "overview_age_filter": "All",
        "overview_pos_filter": "All",
        "overview_team_filter": "All",
        "overview_league_filter": "All",
        "overview_minutes_filter": 0,
        "overview_num_players_filter": 100,
        "overview_do_reset": False,
    }

    # Inicializar claves en session_state
    for key, value in overview_defaults.items():
        st.session_state.setdefault(key, value)

    # Resetear filtros si el flag está activo
    if st.session_state["overview_do_reset"]:

        # Restaurar valores iniciales
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

    # Crear layout de filtros
    overview_col1, overview_col2, overview_col3, overview_col4, overview_col5, overview_col6 = st.columns([2, 2, 2, 2, 2, 2])

    # Aplicar filtros reutilizables
    overview_filtered_df = apply_player_filters_overview_rk(
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
            key="overview_num_players_filter"
        )

    # Limitar número de jugadores mostrados
    overview_filtered_df = overview_filtered_df.head(overview_num_players)

    # Insertar separador visual
    st.divider()

    # Mostrar dataframe interactivo
    st.dataframe(
        overview_filtered_df,
        hide_index=True,
        column_config={
            "Id_player": st.column_config.Column(pinned="left"),
            "Player": st.column_config.Column(pinned="left"),
        }
    )

    # Crear CSV en memoria
    csv_buffer = io.StringIO()
    overview_filtered_df.to_csv(csv_buffer, index=False)

    # Botón de descarga con log
    st.download_button(
        label="📥 Download CSV",
        data=csv_buffer.getvalue(),
        file_name="players_overview.csv",
        mime="text/csv",
        on_click=log_download_event,
        kwargs={
            "page_name": "overview",
            "prefix": "overview"
        }
    )

    # Botón para resetear filtros
    if st.button("🔄 Reset filters"):

        # Activar flag de reset
        st.session_state["overview_do_reset"] = True

        # Recargar la app
        st.rerun()