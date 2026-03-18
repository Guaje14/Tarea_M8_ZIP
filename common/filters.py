# ============================================
# Common -> filters
# ============================================

# Importar librerías
import pandas as pd
import streamlit as st

# Aplicar filtros encadenados a un dataframe de jugadores
def apply_player_filters(df, col1, col2, col3, col4, col5, prefix):

    # Crear claves únicas para guardar filtros en session_state
    minutes_key = f"{prefix}_minutes_filter"
    league_key = f"{prefix}_league_filter"
    team_key = f"{prefix}_team_filter"
    age_key = f"{prefix}_age_filter"
    pos_key = f"{prefix}_pos_filter"

    # Filtro de % de minutos jugados
    with col5:
        minutes_filter = st.slider(
            "% Min Played",        
            0,                     
            100,                   
            key=minutes_key        
        )
    df_base = df.copy()

    # Convertir columnas a numéricas
    df_base["stats_Min"] = pd.to_numeric(df_base["stats_Min"], errors="coerce")
    df_base["stats_Age"] = pd.to_numeric(df_base["stats_Age"], errors="coerce")

    # Obtener máximo de minutos en el dataset
    max_min = df_base["stats_Min"].max()

    # Filtrar jugadores según % de minutos jugados
    df_base = df_base[
        df_base["stats_Min"] >= max_min * minutes_filter / 100
    ]

    # Filtro de Liga
    with col1:
        leagues = ["All"] + sorted(df_base["stats_Comp"].dropna().unique())
        st.selectbox("League", leagues, key=league_key)
    df_league = df_base.copy()

    # Filtrar por liga si no es "All"
    if st.session_state[league_key] != "All":
        df_league = df_league[
            df_league["stats_Comp"] == st.session_state[league_key]
        ]

    # Filtro de Equipo
    with col2:
        teams = ["All"] + sorted(df_league["stats_Squad"].dropna().unique())
        st.selectbox("Team", teams, key=team_key)
    df_team = df_league.copy()

    # Filtrar por equipo si no es "All"
    if st.session_state[team_key] != "All":
        df_team = df_team[
            df_team["stats_Squad"] == st.session_state[team_key]
        ]

    # Filtro de Edad
    with col3:
        ages = sorted(df_team["stats_Age"].dropna().unique())
        st.selectbox("Age", ["All"] + ages, key=age_key)
    df_age = df_team.copy()

    # Filtrar por edad si se selecciona una
    if st.session_state[age_key] != "All":
        df_age = df_age[
            df_age["stats_Age"] == st.session_state[age_key]
        ]

    # Filtro de Posición
    with col4:

        # Posiciones disponibles en el dataset actual
        available_pos = df_age["stats_Pos"].dropna().unique()

        # Orden lógico de posiciones
        pos_options = ["All"] + [
            p for p in ["GK", "DF", "MF", "FW"] if p in available_pos
        ]

        st.selectbox("Position", pos_options, key=pos_key)
    df_final = df_age.copy()

    # Filtrar por posición si no es "All"
    if st.session_state[pos_key] != "All":
        df_final = df_final[
            df_final["stats_Pos"] == st.session_state[pos_key]
        ]

    # Devolver dataframe tras aplicar todos los filtros
    return df_final