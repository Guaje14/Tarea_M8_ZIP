# ============================================
# Page Ranking
# ============================================

# Importar librerías 
import streamlit as st
from PIL import Image
import difflib
import io

# Importar rutas de configuración
from common.config import (
    ASSETSIMG
)

# Importar funciones de datos y filtros
from controllers.db_controller import load_stats_players_fbref
from common.filters import apply_player_filters_overview_rk
from controllers.logs_export_csv import log_download_event

# Función que da cómo resultado la página Ranking
def page_rk():

    # Crear 3 columnas para centrar la imagen
    rk_imgcol1, rk_imgcol2, rk_imgcol3 = st.columns([3, 2, 3])

    with rk_imgcol2:

        # Cargar imagen desde la carpeta assets
        rk_img_podium = Image.open(ASSETSIMG / "Freepick Podium.png")

        # Mostrar imagen en Streamlit
        st.image(rk_img_podium, width=120)

    # Título de la página
    st.header("Interactive Player Filtering")

    # Cargar datos desde la base de datos
    rk_df_players = load_stats_players_fbref()

    # Definir valores iniciales de los filtros
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

    # Inicializar claves en session_state
    for key, value in rk_defaults.items():
        st.session_state.setdefault(key, value)

    # Resetear filtros si el flag está activo
    if st.session_state["rk_do_reset"]:

        # Restaurar valores iniciales
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

    # Crear layout de la página
    rk_col1, rk_col2, rk_col3, rk_col4, rk_col5, rk_col6 = st.columns([2, 2, 2, 2, 2, 2])

    # Aplicar filtros reutilizables
    rk_filtered_df = apply_player_filters_overview_rk(
        rk_df_players,
        rk_col1,
        rk_col2,
        rk_col3,
        rk_col4,
        rk_col5,
        prefix="rk"
    ).copy()

    # Slider para limitar número de jugadores mostrados
    with rk_col6:
        rk_num_players = st.slider(
            "N° Players",
            0,
            100,
            key="rk_num_players_filter"
        )

    # Input para elegir estadística de ranking
    rk_typed_stat = st.text_input(
        "Enter the stat to sort:",
        value=st.session_state["rk_typed_stat"],
        placeholder="Write a stat..."
    )

    # Mostrar ayuda con prefijos de columnas
    st.caption(
        "Categories: possession_, defense_, misc_, stats_, playingtime_, passing_, shooting_, gca_"
    )

    # Guardar texto escrito
    st.session_state["rk_typed_stat"] = rk_typed_stat

    # Obtener columnas numéricas válidas
    rk_all_stats = rk_df_players.select_dtypes(include="number").columns.tolist()

    # Buscar sugerencias automáticas
    if rk_typed_stat:

        rk_closest = difflib.get_close_matches(
            rk_typed_stat,
            rk_all_stats,
            n=7,
            cutoff=0.7
        )

        if rk_closest:

            st.info("Select stat:")

            # Mostrar selector en móvil
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

            # Mostrar botones en desktop
            else:
                rk_cols_btn = st.columns(min(len(rk_closest), 6))

                for i, c in enumerate(rk_closest[:6]):
                    if rk_cols_btn[i].button(c):
                        st.session_state["rk_selected_stat"] = c
                        st.session_state["rk_typed_stat"] = c

        else:
            st.warning("No similar stats found")

    # Obtener estadística final seleccionada
    rk_stat_col = st.session_state["rk_selected_stat"]

    # Mostrar la estadística elegida
    if rk_stat_col:
        st.success(f"Will be used: **{rk_stat_col}**")

    # Calcular ranking por estadística elegida
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
            rk_filtered_df["rk_rank_num"] = range(1, len(rk_filtered_df) + 1)

    # Ordenar ranking
    rk_filtered_df = rk_filtered_df.sort_values("rk_rank_num")

    # Limitar número de jugadores después de ordenar
    rk_filtered_df = rk_filtered_df.head(rk_num_players)

    # Función para añadir emoji al Top 3
    def rk_ranking_emoji(r):
        if r == 1:
            return "🥇"
        elif r == 2:
            return "🥈"
        elif r == 3:
            return "🥉"
        else:
            return int(r)

    # Crear columna visual de ranking
    rk_filtered_df["Rk"] = rk_filtered_df["rk_rank_num"].apply(rk_ranking_emoji)

    # Reordenar columnas
    rk_cols = rk_filtered_df.columns.tolist()
    rk_cols.insert(0, rk_cols.pop(rk_cols.index("Rk")))
    rk_filtered_df = rk_filtered_df[rk_cols]

    # Eliminar columna auxiliar
    rk_filtered_df = rk_filtered_df.drop(columns=["rk_rank_num"])

    # Insertar separador visual
    st.divider()

    # Mostrar dataframe interactivo
    st.dataframe(
        rk_filtered_df,
        hide_index=True,
        column_config={
            "Rk": st.column_config.Column(pinned="left"),
            "Player": st.column_config.Column(pinned="left"),
        }
    )

    # Crear CSV en memoria
    csv_buffer = io.StringIO()
    rk_filtered_df.to_csv(csv_buffer, index=False)

    # Botón de descarga con log
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