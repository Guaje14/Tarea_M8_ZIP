# ============================================
# Page Radar
# ============================================

# Importar librerías 
import streamlit as st
from PIL import Image
import difflib
import plotly.graph_objects as go
import numpy as np
from scipy import stats
import pandas as pd
import streamlit.components.v1 as components
from fpdf import FPDF
import io
import base64
import matplotlib.pyplot as plt
import plotly.io as pio

# Importar rutas de configuración
from common.config import (
    ASSETSIMG, ASSETSFONTS
)

# Importar funciones de datos y marca de agua
from controllers.db_controller import load_stats_players_fbref
from common.pdf_utils import get_watermark, generate_radar_matplotlib
    
# Función que da cómo resultado la página Radar
def page_radar(): 
    
    # Añadir CSS de impresión
    st.markdown(
    """
    <style>

    /* estilos solo cuando se imprime */
    @media print {
        
        body {
            zoom: 0.7;
        }

        /* ocultar sidebar */
        section[data-testid="stSidebar"] {
            display: none;
        }

        /* ocultar menú superior de streamlit */
        header {
            display: none;
        }

        /* ocultar footer */
        footer {
            display: none;
        }

        /* expandir contenido principal */
        .main {
            margin-left: 0px;
            width: 100%;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
    )
    
    # Se crean 3 columnas para centrar la imagen
    radar_imgcol1, radar_imgcol2, radar_imgcol3 = st.columns([3, 2, 3])
    
    with radar_imgcol2:
    
        # Se carga una imagen desde la carpeta assets
        freepick_pieChart = Image.open(ASSETSIMG / "Freepick PieChart.png")
        
        # Se muestra la imagen en Streamlit
        st.image(freepick_pieChart, width=120) 
    
    # Título de la página
    st.header("Player Performance Radar")  
    
    # Cargar datos desde la DB
    radar_df = load_stats_players_fbref()
    
    # Rellenar los valores faltantes
    radar_df = radar_df.fillna(0)
        
    # Valores por defecto para session_state 
    radar_defaults = {
        "leagueA": "All",
        "teamA": "All",
        "posA": "All",
        "playerA": "All",
        "leagueB": "All",
        "teamB": "All",
        "posB": "All",
        "playerB": "All",
        "radar_do_reset": False,          # Flag para resetear filtros
        "chart_type": "",
        "method": "",
        "typed_stat": "",           # Texto introducido por el usuario para la stat
        "selected_stats": [],       # Stat final seleccionada
        "is_mobile": False,         # Flag para modo móvil (responsive)
    } 
    
    # Inicializar session_state si no existe
    for key, value in radar_defaults.items():
        if key not in st.session_state or st.session_state[key] is None:
            st.session_state[key] = value

    # Aplicar reset si está activado 
    if st.session_state["radar_do_reset"]:
        # Reiniciar filtros
        st.session_state["leagueA"] = "All"
        st.session_state["teamA"] = "All"
        st.session_state["posA"] = "All"
        st.session_state["playerA"] = "All"
        st.session_state["leagueB"] = "All"
        st.session_state["teamB"] = "All"
        st.session_state["posB"] = "All"
        st.session_state["playerB"] = "All"
        
        # Reiniciar input de stat
        st.session_state["typed_stat_radar"] = ""
        st.session_state["selected_stats_radar"] = []

        # Desactivar flag
        st.session_state["do_reset_radar"] = False

        # Recarga la página para actualizar widgets
        st.rerun()

    # Layout de la página
    radar_col1, radar_col2, radar_col3 = st.columns([1.5, 2.5, 1.5])  # A: izquierda, radar: centro, B: derecha

    pos_order = ["All", "GK", "DF", "MF", "FW"]  # orden fijo de posiciones

    # Formularios de los Jugadores A y B
    with radar_col1:
        st.subheader("Player A")

        # Liga A
        leaguesA = ["All"] + sorted(radar_df["stats_Comp"].unique())
        leagueA = st.selectbox("League A", leaguesA, index=0, key="leagueA")

        # Equipo A
        if leagueA == "All":
            teamsA = ["All"] + sorted(radar_df["stats_Squad"].unique())
        else:
            teamsA = ["All"] + sorted(radar_df[radar_df["stats_Comp"] == leagueA]["stats_Squad"].unique())
        teamA = st.selectbox("Team A", teamsA, index=0, key="teamA")

        # Posición A
        if leagueA == "All" and teamA == "All":
            available_posA = radar_df["stats_Pos"].unique()
        elif teamA == "All":
            available_posA = radar_df[radar_df["stats_Comp"] == leagueA]["stats_Pos"].unique()
        else:
            available_posA = radar_df[(radar_df["stats_Comp"] == leagueA) & (radar_df["stats_Squad"] == teamA)]["stats_Pos"].unique()
        available_posA = ["All"] + [p for p in pos_order if p in available_posA]
        posA = st.selectbox("Position A", available_posA, index=0, key="posA")

        # Filtrar jugadores
        playersA_df = radar_df.copy()
        if leagueA != "All":
            playersA_df = playersA_df[playersA_df["stats_Comp"] == leagueA]
        if teamA != "All":
            playersA_df = playersA_df[playersA_df["stats_Squad"] == teamA]
        if posA != "All":
            playersA_df = playersA_df[playersA_df["stats_Pos"] == posA]

        # Agrupar por jugador y sumar minutos
        players_info_A = (
            playersA_df
            .groupby("Player", as_index=False)["stats_Min"]
            .sum()
        )

        # Crear etiqueta segura
        players_info_A["label"] = (
            players_info_A["Player"] + " | " +
            players_info_A["stats_Min"]
                .fillna(0)
                .round(0)
                .astype(int)
                .astype(str)
            + " min"
        )

        # Diccionario label -> Player
        label_to_player_A = dict(zip(players_info_A["label"], players_info_A["Player"]))

        # Selector Player A
        playerA_label = st.selectbox(
            "Player A",
            ["All"] + list(label_to_player_A.keys()),
            index=0,
            key="playerA"
        )

        playerA = label_to_player_A[playerA_label] if playerA_label != "All" else "All"

    with radar_col3:
        st.subheader("Player B")

        # Liga B
        leaguesB = ["All"] + sorted(radar_df["stats_Comp"].unique())
        leagueB = st.selectbox("League B", leaguesB, index=0, key="leagueB")

        # Equipo B
        if leagueB == "All":
            teamsB = ["All"] + sorted(radar_df["stats_Squad"].unique())
        else:
            teamsB = ["All"] + sorted(radar_df[radar_df["stats_Comp"] == leagueB]["stats_Squad"].unique())
        teamB = st.selectbox("Team B", teamsB, index=0, key="teamB")

        # Posición B
        if leagueB == "All" and teamB == "All":
            available_posB = radar_df["stats_Pos"].unique()
        elif teamB == "All":
            available_posB = radar_df[radar_df["stats_Comp"] == leagueB]["stats_Pos"].unique()
        else:
            available_posB = radar_df[(radar_df["stats_Comp"] == leagueB) & (radar_df["stats_Squad"] == teamB)]["stats_Pos"].unique()
        available_posB = ["All"] + [p for p in pos_order if p in available_posB]
        posB = st.selectbox("Position B", available_posB, index=0, key="posB")

        # Filtrar jugadores
        playersB_df = radar_df.copy()
        if leagueB != "All":
            playersB_df = playersB_df[playersB_df["stats_Comp"] == leagueB]
        if teamB != "All":
            playersB_df = playersB_df[playersB_df["stats_Squad"] == teamB]
        if posB != "All":
            playersB_df = playersB_df[playersB_df["stats_Pos"] == posB]

        # Agrupar por jugador y sumar minutos
        players_info_B = (
            playersB_df
            .groupby("Player", as_index=False)["stats_Min"]
            .sum()
        )

        # Crear etiqueta segura
        players_info_B["label"] = (
            players_info_B["Player"] + " | " +
            players_info_B["stats_Min"]
                .fillna(0)
                .round(0)
                .astype(int)
                .astype(str)
            + " min"
        )

        # Diccionario label -> Player
        label_to_player_B = dict(zip(players_info_B["label"], players_info_B["Player"]))

        # Selector Player B
        playerB_label = st.selectbox(
            "Player B",
            ["All"] + list(label_to_player_B.keys()),
            index=0,
            key="playerB"
        )

        playerB = label_to_player_B[playerB_label] if playerB_label != "All" else "All"
        
    # Espacio para el Plot
    with radar_col2:
        st.subheader("Pizza Chart")

        # Opciones con placeholder como primer valor
        chart_type_options = ["-- Select type --", "Compare Players", "The Best Player"]
        method_options = ["-- Select method --", "Standard", "Percentil"]

        # Selectboxes
        chart_type = st.selectbox("Select type of plot", chart_type_options, index=0, key="chart_type")
        method = st.selectbox("Select Method", method_options, index=0, key="method")

        # Convertir placeholder en None para lógica interna
        chart_type_val = None if chart_type == chart_type_options[0] else chart_type
        method_val = None if method == method_options[0] else method
        
        # Explicaciones según el método
        method_explanations = {
            "Standard": "Shows the accumulated absolute values for each player. Reflects the total impact over the season, so it is strongly influenced by minutes played. Recommended for comparing players with a similar volume of minutes.",
            "Percentil": "Indicates the player's relative position (0–100) compared to other players in the same position and with similar minutes played. Allows evaluating performance within their actual role (starter, rotation, or substitute). A high percentile does not imply higher total impact, but better relative performance in context."
        }

        # Mostrar explicación si hay método seleccionado
        if method_val:
            st.info(method_explanations[method_val])
        
        radar_placeholder = st.empty()
        st.info("Select up to 6 stats")

    # Selección de Estadísticas
    st.subheader("Select statistics to compare (max 6)")

    # Input de stat  
    typed_stat_radar = st.text_input(
        "Write a stat:",
        value=st.session_state.get("typed_stat_radar", ""),
        placeholder="Write a stat..."
    )
    st.session_state["typed_stat_radar"] = typed_stat_radar

    st.caption("Categories:  possession_,  defense_,  misc_,  stats_,  playingtime_,  passing_,  shooting_,  gca_")

    # Inicializar lista de stats seleccionadas para radar si no existe
    if "selected_stats_radar" not in st.session_state:
        st.session_state["selected_stats_radar"] = []

    selected_stats = st.session_state["selected_stats_radar"]

    # Columnas válidas 
    common_stats = radar_df.select_dtypes(include="number").columns.tolist()
    common_stats = [c for c in common_stats if c not in ["stats_Min", "stats_Age"]]

    # Autocompletar estadísticas y permitir agregarlas con botones
    if typed_stat_radar and common_stats:
        
        # Buscar coincidencias cercanas entre lo escrito y estadísticas comunes
        closest = difflib.get_close_matches(typed_stat_radar, common_stats, n=6, cutoff=0.5)
        
        if closest:
            # Crear hasta 6 columnas para los botones
            st.info("Select stat to add:")  
            cols_btn = st.columns(min(len(closest), 6))  
            
            for i, c in enumerate(closest[:6]):
                
                # Crear un botón para cada estadística cercana
                if cols_btn[i].button(c):  
                    
                    # Añadir la estadística seleccionada si no está y hay menos de 6
                    if c not in selected_stats and len(selected_stats) < 6:
                        selected_stats.append(c)
                    
                        # Guardar cambios en el estado de sesión de Streamlit
                        st.session_state["selected_stats_radar"] = selected_stats
                        st.session_state["typed_stat_radar"] = ""  # Limpiar input tras añadir
                        
    # Mostrar stats seleccionadas
    if selected_stats:
        st.success(f"Stats selected: {', '.join(selected_stats)}")

    # Generar gráficos de radar si hay tipo de gráfico, estadísticas seleccionadas y ambos jugadores
    if chart_type_val and selected_stats and playerA and playerB:

        # Configuración visual del radar
        RADAR_MAX = 100        # Límite visual de las barras
        RADAR_PAD = 18         # Espacio extra para textos
        TEXT_PAD = 6           # Separación barra → texto

        r_min_global = 0
        r_max_global = RADAR_MAX + RADAR_PAD

        rA_vals, rB_vals = [], []  # Valores normalizados para cada jugador
        textA, textB = [], []      # Texto a mostrar en cada barra del radar

        for stat in selected_stats:
            
            # Obtener valor de cada estadística para ambos jugadores
            valA = radar_df.loc[radar_df["Player"] == playerA, stat].values[0]
            valB = radar_df.loc[radar_df["Player"] == playerB, stat].values[0]

            # Obtener minutos de cada jugador
            minA = radar_df.loc[radar_df["Player"] == playerA, "stats_Min"].values[0]
            minB = radar_df.loc[radar_df["Player"] == playerB, "stats_Min"].values[0]

            # Método Standard: normaliza cada estadística entre min y max de todos los jugadores
            if method_val == "Standard":
                textA.append(f"{valA:.2f}")  
                textB.append(f"{valB:.2f}")

                stat_series = pd.to_numeric(radar_df[stat], errors="coerce")
                stat_min = stat_series.min()
                stat_max = stat_series.max()

                if stat_max > stat_min:
                    rA = (valA - stat_min) / (stat_max - stat_min) * 100
                    rB = (valB - stat_min) / (stat_max - stat_min) * 100
                else:
                    rA = rB = 0

                r_min, r_max = 0, 100

            # Método Percentil: compara jugadores con su posición y rango de mínimos
            elif method_val == "Percentil":
            
                # Minutos jugados de los dos jugadores
                minA = radar_df.loc[radar_df["Player"] == playerA, "stats_Min"].values[0]
                minB = radar_df.loc[radar_df["Player"] == playerB, "stats_Min"].values[0]

                # Calcular la "media de la media" (threshold)
                threshold = (minA + minB) / 2 / 2  # es decir, un cuarto de la suma de minA+minB

                # Para cada estadística
                for stat in selected_stats:
                    # Valor del jugador
                    valA = radar_df.loc[radar_df["Player"] == playerA, stat].values[0]
                    valB = radar_df.loc[radar_df["Player"] == playerB, stat].values[0]

                    # Normalización a 90 minutos (evitar división por 0)
                    valA_norm = valA / minA * 90 if minA > 0 else 0
                    valB_norm = valB / minB * 90 if minB > 0 else 0

                    # Filtrar jugadores de la misma posición y con suficiente tiempo
                    df_baseA = radar_df[(radar_df["stats_Pos"] == posA) & (radar_df["stats_Min"] >= threshold)]
                    df_baseB = radar_df[(radar_df["stats_Pos"] == posB) & (radar_df["stats_Min"] >= threshold)]

                    # Calcular percentil (fallback a 50 si la muestra está vacía)
                    if not df_baseA.empty:
                        rA = stats.percentileofscore(df_baseA[stat] / df_baseA["stats_Min"] * 90, valA_norm, kind="rank")
                    else:
                        rA = 50

                    if not df_baseB.empty:
                        rB = stats.percentileofscore(df_baseB[stat] / df_baseB["stats_Min"] * 90, valB_norm, kind="rank")
                    else:
                        rB = 50

                    # Guardar siempre valores y textos para el radar
                    rA_vals.append(rA)
                    rB_vals.append(rB)
                    textA.append(f"{rA:.0f}")
                    textB.append(f"{rB:.0f}")

        # Configuración de ángulos y anchuras para el radar
        n = len(selected_stats)
        angles = np.linspace(0, 360, n, endpoint=False)    
        widths = [360/n*0.9]*n                             

        # Crear figura vacía de Plotly
        fig = go.Figure()

        # Tipo de gráfico: Comparación de jugadores
        if chart_type_val == "Compare Players":
            
            # Calcular opacidades dinámicas para resaltar cuál jugador gana en cada stat
            opacities_A = [0.85 if a>=b else 0.5 for a,b in zip(rA_vals, rB_vals)]
            opacities_B = [0.85 if b>=a else 0.5 for a,b in zip(rA_vals, rB_vals)]

            # Agregar barras polares para el jugador A
            fig.add_trace(go.Barpolar(
                r=rA_vals,           
                base=[0]*n,          
                theta=angles,        
                width=widths,        
                name=playerA,        
                marker=dict(
                    color="#1f77b4",     
                    opacity=opacities_A 
                ))
            )
            
            # Agregar barras polares para el jugador B
            fig.add_trace(go.Barpolar(
                r=rB_vals, 
                base=[0]*n,
                theta=angles, 
                width=widths,
                name=playerB, 
                marker=dict(
                    color="#d62728",     
                    opacity=opacities_B
                ))
            )

            # Añadir textos con valores de cada stat
            ANGLE_OFFSET = 3  

            for i in range(n):
                
                # Texto para jugador A
                fig.add_trace(go.Scatterpolar(
                    r=[min(rA_vals[i] + TEXT_PAD, RADAR_MAX + RADAR_PAD - 2)],  
                    theta=[angles[i] - ANGLE_OFFSET],  
                    mode="text", 
                    text=[textA[i]],                  
                    showlegend=False,                  
                    textfont=dict(size=11, color="#1f77b4")
                ))

                # Texto para jugador B
                fig.add_trace(go.Scatterpolar(
                    r=[min(rB_vals[i] + TEXT_PAD, RADAR_MAX + RADAR_PAD - 2)],
                    theta=[angles[i] + ANGLE_OFFSET],  
                    mode="text",
                    text=[textB[i]],
                    showlegend=False,
                    textfont=dict(size=11, color="#d62728")
                ))

        # Tipo de gráfico: The Best Player
        elif chart_type_val == "The Best Player":
            
            # Dibujar solo la barra del jugador que gana en cada stat
            plotted_players = set()  
            for i in range(n):
                if rA_vals[i] >= rB_vals[i]:
                    color, val, text = "#1f77b4", rA_vals[i], textA[i]
                    player_name = playerA
                else:
                    color, val, text = "#d62728", rB_vals[i], textB[i]
                    player_name = playerB

                # Mostrar leyenda solo una vez por jugador
                show_legend = False
                if player_name not in plotted_players:
                    show_legend = True
                    plotted_players.add(player_name)

                # Dibujar la barra polar solo del jugador ganador en esta stat
                fig.add_trace(go.Barpolar(
                    r=[val], 
                    theta=[angles[i]], 
                    width=[widths[i]],
                    name=player_name, 
                    marker_color=color, 
                    opacity=0.85,
                    showlegend=show_legend)
                )
                
                # Añadir texto del valor del ganador
                fig.add_trace(go.Scatterpolar(
                    r=[val + r_max_global*0.05],   
                    theta=[angles[i]],
                    mode="text", 
                    text=[text], 
                    showlegend=False,
                    textfont=dict(size=11,color="black"))
                )

        # Configuración general del layout del radar
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    range=[0, RADAR_MAX + RADAR_PAD],  
                    showticklabels=True,                
                    showline=False,                     
                    gridcolor="rgba(0,0,0,0.1)"       
                ),
                angularaxis=dict(
                    tickmode="array",
                    tickvals=angles,       
                    ticktext=selected_stats, 
                    showline=False
                )
            ),
            legend=dict(
                orientation="h",     
                yanchor="bottom",
                y=1.15,              
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=90, b=40)  
        )

        # Mostrar gráfico en el placeholder de Streamlit
        radar_placeholder.plotly_chart(fig, use_container_width=True)

    # Botón para resetear formularios
    if st.button("🔄 Reset Forms"):
        st.session_state["radar_do_reset"] = True  
        st.rerun()      
    
    # Botón para imprimir la página
    components.html(
    """
    <button onclick="parent.window.print()" style="
        padding:8px 14px;
        font-size:14px;
        cursor:pointer;
        background-color:#2563eb;
        color:white;
        border:none;
        border-radius:6px;">
        🖨️ Print Page
    </button>
    """,
    height=55
    )                           

    # Botón en Streamlit para preparar el PDF
    if st.button("⚙️ Prepare PDF") and chart_type_val and playerA and playerB:

        # Generar el radar usando la función anterior
        fig_mat = generate_radar_matplotlib(
            rA_vals=rA_vals,
            rB_vals=rB_vals,
            selected_stats=selected_stats,
            playerA=playerA,
            playerB=playerB,
            chart_type_val=chart_type_val,
            textA=textA,
            textB=textB
        )

        # Guardar la figura en un buffer en memoria como PNG
        radar_buffer = io.BytesIO()
        fig_mat.savefig(radar_buffer, format="png", bbox_inches='tight', dpi=200)
        plt.close(fig_mat)          # Cerrar figura para liberar memoria
        radar_buffer.seek(0)        # Reposicionar puntero al inicio del buffer

        # Crear un PDF nuevo
        pdf_radar = FPDF()
        pdf_radar.add_page()        # Añadir página al PDF

        # Configurar fuente
        pdf_radar.add_font("DejaVu", "", str(ASSETSFONTS / "DejaVuSans.ttf"), uni=True)
        pdf_radar.set_font("DejaVu", "", 12)

        # Título del PDF con usuario, tipo de radar y método
        usuario_radar = st.session_state.get("user").username if st.session_state.get("user") else "Desconocido"
        title_radar = f"User: {usuario_radar} | Radar Type: {chart_type_val} | Method: {method_val or 'N/A'}"
        pdf_radar.multi_cell(0, 10, title_radar, align="C")
        pdf_radar.ln(5)             
        
        # Insertar la imagen del radar en el PDF
        pdf_radar.image(radar_buffer, x=30, w=150)

        # Añadir marca de agua o logo
        logo_path_radar = get_watermark(alpha=10)
        pdf_radar.image(logo_path_radar, x=55, y=100, w=100)

        # Convertir PDF a bytes y luego a base64 para descargar en Streamlit
        pdf_bytes_radar = pdf_radar.output(dest="S")
        pdf_base64_radar = base64.b64encode(pdf_bytes_radar).decode("utf-8")

        # Crear botón HTML para descargar el PDF
        components.html(
            f"""
            <a href="data:application/pdf;base64,{pdf_base64_radar}" download="radar.pdf">
                <button style="
                    padding:8px 14px;
                    font-size:14px;
                    cursor:pointer;
                    background-color:#dc2626;
                    color:white;
                    border:none;
                    border-radius:6px;">
                    📄 Export Radar to PDF
                </button>
            </a>
            """,
            height=55
        )