# ============================================
# Page Ranking
# ============================================

# Importar librerías 
import streamlit as st
from PIL import Image
import difflib
import pandas as pd
import io

# Importar rutas de configuración
from common.config import (
    ASSETSIMG
)

# Importar funciones de datos y filtros
from controllers.db_controller import load_stats_players_fbref
from common.filters import apply_player_filters
from controllers.logs_export_csv import log_download_event

# Función que da cómo resultado la página Ranking
def page_rk():

    # Se crean 3 columnas para centrar la imagen
    rk_imgcol1, rk_imgcol2, rk_imgcol3 = st.columns([3, 2, 3])

    with rk_imgcol2:

        # Se carga una imagen desde la carpeta assets
        rk_img_podium = Image.open(ASSETSIMG / "Freepick Podium.png")

        # Se muestra la imagen en Streamlit
        st.image(rk_img_podium, width=120)

    # Título de la página
    st.header("Interactive Player Filtering")
    
    # Cargar datos desde la base de datos
    rk_df_players = load_stats_players_fbref()

    # Diccionario con los valores iniciales de los filtros
    rk_defaults = {
        "rk_age_filter": "All",
        "rk_pos_filter": "All",
        "rk_team_filter": "All",
        "rk_league_filter": "All",
        "rk_minutes_filter": 0,
        "rk_num_players_filter": 100,
        "rk_do_reset": False,
        "rk_typed_stat": "",
        "rk_selected_stat": None,
    }

    # Si alguna variable no existe en session_state se crea
    for key, value in rk_defaults.items():
        st.session_state.setdefault(key, value)

    # Si el botón de reset fue presionado
    if st.session_state["rk_do_reset"]:
        
        # Restaurar todos los filtros a valores iniciales
        st.session_state["rk_age_filter"] = "All"
        st.session_state["rk_pos_filter"] = "All"
        st.session_state["rk_team_filter"] = "All"
        st.session_state["rk_league_filter"] = "All"
        st.session_state["rk_minutes_filter"] = 0
        st.session_state["rk_num_players_filter"] = 100
        st.session_state["rk_typed_stat"] = ""
        st.session_state["rk_selected_stat"] = None

        # Desactivar flag de reset
        st.session_state["rk_do_reset"] = False

        # Recargar la app
        st.rerun()

    # Layout de la página
    rk_col1, rk_col2, rk_col3, rk_col4, rk_col5, rk_col6 = st.columns([2,2,2,2,2,2])

    # Aplicar filtros reutilizables
    rk_filtered_df = apply_player_filters(
        rk_df_players,
        rk_col1,
        rk_col2,
        rk_col3,
        rk_col4,
        rk_col5,
        prefix="rk"
    )

    # Slider para limitar número de jugadores
    with rk_col6:

        rk_num_players = st.slider(
            "N° Players",
            0,
            100,
            st.session_state["rk_num_players_filter"],
            
            # KEY única para evitar conflictos con otras páginas
            key="rk_num_players_filter"
        )

    # Limitar número de jugadores mostrados
    rk_filtered_df = rk_filtered_df.head(rk_num_players)

    # Input para elegir estadística de ranking
    rk_typed_stat = st.text_input(
        "Enter the stat to sort:",
        value=st.session_state["rk_typed_stat"],
        placeholder="Write a stat..."
    )

    st.caption(
        "Categories: possession_, defense_, misc_, stats_, playingtime_, passing_, shooting_, gca_"
    )

    st.session_state["rk_typed_stat"] = rk_typed_stat

    # Columnas válidas para ranking
    rk_all_stats = rk_df_players.select_dtypes(include="number").columns.tolist()
    
    # Sugerencias automáticas de estadística
    if rk_typed_stat:

        rk_closest = difflib.get_close_matches(
            rk_typed_stat,
            rk_all_stats,
            n=7,
            cutoff=0.7
        )

        if rk_closest:

            st.info("Select stat:")

            # Usar la variable centralizada 'is_mobile' de common/device.py
            if st.session_state["is_mobile"]:

                rk_selected = st.selectbox(
                    "Suggestions",
                    rk_closest,
                    index=None,
                    placeholder="Select stat..."
                )

                if rk_selected:
                    st.session_state["rk_selected_stat"] = rk_selected
                    st.session_state["rk_typed_stat"] = rk_selected

            else:

                rk_cols_btn = st.columns(min(len(rk_closest), 6))

                for i, c in enumerate(rk_closest[:6]):

                    if rk_cols_btn[i].button(c):
                        st.session_state["rk_selected_stat"] = c
                        st.session_state["rk_typed_stat"] = c

    # Determinar estadística final
    rk_stat_col = st.session_state["rk_selected_stat"]

    if rk_stat_col:
        st.success(f"Will be used: **{rk_stat_col}**")

    # Generar ranking
    if rk_stat_col and rk_stat_col in rk_filtered_df.columns:

        rk_filtered_df["rk_rank_num"] = rk_filtered_df[rk_stat_col].rank(
            ascending=False,
            method="min"
        )

    else:

        rk_num_cols = rk_filtered_df.select_dtypes(include="number").columns.tolist()

        if rk_num_cols:

            rk_filtered_df["rk_rank_num"] = rk_filtered_df[rk_num_cols[0]].rank(
                ascending=False,
                method="min"
            )

        else:

            rk_filtered_df["rk_rank_num"] = range(1, len(rk_filtered_df)+1)

    rk_filtered_df = rk_filtered_df.sort_values("rk_rank_num")
    
    # Emojis para Top 3
    def rk_ranking_emoji(r):
        if r == 1:
            return "🥇"
        elif r == 2:
            return "🥈"
        elif r == 3:
            return "🥉"
        else:
            return int(r)

    rk_filtered_df["Rk"] = rk_filtered_df["rk_rank_num"].apply(rk_ranking_emoji)

    # Reordenar columnas
    rk_cols = rk_filtered_df.columns.tolist()
    rk_cols.insert(0, rk_cols.pop(rk_cols.index("Rk")))
    rk_filtered_df = rk_filtered_df[rk_cols]
    rk_filtered_df = rk_filtered_df.drop(columns=["rk_rank_num"])

    # Línea visual separadora
    st.divider()

    # Dataframe interactivo de Streamlit
    st.dataframe(
        rk_filtered_df,
        hide_index=True,
        column_config={
            "Rk": st.column_config.Column(pinned="left"),
            "Player": st.column_config.Column(pinned="left"),
        }
    )
    
    # Crear CSV
    csv_buffer = io.StringIO()
    rk_filtered_df.to_csv(csv_buffer, index=False)

    # Botón descarga + log
    st.download_button(
        label="📥 Download CSV",
        data=csv_buffer.getvalue(),
        file_name="players_ranking.csv",
        mime="text/csv",
        on_click=log_download_event,
        kwargs={
            "page_name": "ranking",
            "prefix": "rk",
            "extra_data": {
                "selected_stat": st.session_state.get("rk_selected_stat")
            }
        }
    )
        
    # Botón para resetear filtros
    if st.button("🔄 Reset filters"):

        # Activar flag de reset
        st.session_state["rk_do_reset"] = True

        # Recargar la página
        st.rerun()