# ============================================
# Page Lineup
# ============================================

# Importar librerías 
import streamlit as st
import pandas as pd
import os
from PIL import Image
import matplotlib.pyplot as plt
import uuid  
import base64
import streamlit.components.v1 as components
from fpdf import FPDF
from io import BytesIO

# Importar rutas de configuración
from common.config import (
    ASSETSIMG, DATA_DIR, ASSETSFONTS
)

# Importar funciones de datos y marca de agua
from controllers.db_controller import load_stats_players_fbref
from common.pdf_utils import get_watermark
    
# Función que da cómo resultado la página Lineup
def page_lineup():
    
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
    lineup_imgcol1, lineup_imgcol2, lineup_imgcol3 = st.columns([3, 2, 3])

    with lineup_imgcol2:

        # Se carga una imagen desde la carpeta assets
        lineup_img_header = Image.open(ASSETSIMG / "Freepick Select.png")
        
        # Se muestra la imagen en Streamlit
        st.image(lineup_img_header, width=120)

    # Título de la página
    st.header("Weekly Best XI")
    
    # Cargar datos desde la DB
    lineup_df_players = load_stats_players_fbref()

    # Lista de sistemas tácticos disponibles
    lineup_sistemas = [
        "1-4-4-2","1-4-3-3","1-3-5-2","1-4-2-3-1","1-5-3-2",
        "1-4-3-2-1","1-3-4-3","1-4-1-4-1","1-3-6-1","1-4-5-1"
    ]

    # Coordenadas normalizadas por sistema
    lineup_posiciones = {

        "1-4-4-2": [
            (0.5, 0.1),                                   # GK
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),      # DEF
            (0.2,0.5),(0.4,0.5),(0.6,0.5),(0.8,0.5),      # MID
            (0.4,0.7),(0.6,0.7)                           # FW
        ],

        "1-4-3-3": [
            (0.5,0.1),
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),
            (0.3,0.5),(0.5,0.5),(0.7,0.5),
            (0.25,0.75),(0.5,0.8),(0.75,0.75)
        ],

        "1-3-5-2": [
            (0.5,0.1),
            (0.3,0.3),(0.5,0.3),(0.7,0.3),
            (0.15,0.5),(0.35,0.5),(0.5,0.5),(0.65,0.5),(0.85,0.5),
            (0.4,0.75),(0.6,0.75)
        ],

        "1-4-2-3-1": [
            (0.5,0.1),
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),
            (0.4,0.45),(0.6,0.45),
            (0.3,0.65),(0.5,0.7),(0.7,0.65),
            (0.5,0.85)
        ],

        "1-5-3-2": [
            (0.5,0.1),
            (0.1,0.3),(0.3,0.3),(0.5,0.3),(0.7,0.3),(0.9,0.3),
            (0.3,0.55),(0.5,0.55),(0.7,0.55),
            (0.4,0.75),(0.6,0.75)
        ],

        "1-4-3-2-1": [
            (0.5,0.1),
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),
            (0.3,0.5),(0.5,0.5),(0.7,0.5),
            (0.4,0.65),(0.6,0.65),
            (0.5,0.85)
        ],

        "1-3-4-3": [
            (0.5,0.1),
            (0.3,0.3),(0.5,0.3),(0.7,0.3),
            (0.2,0.5),(0.4,0.5),(0.6,0.5),(0.8,0.5),
            (0.25,0.75),(0.5,0.8),(0.75,0.75)
        ],

        "1-4-1-4-1": [
            (0.5,0.1),
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),
            (0.5,0.45),
            (0.2,0.6),(0.4,0.6),(0.6,0.6),(0.8,0.6),
            (0.5,0.85)
        ],

        "1-3-6-1": [
            (0.5,0.1),
            (0.3,0.3),(0.5,0.3),(0.7,0.3),
            (0.1,0.5),(0.3,0.5),(0.5,0.5),(0.7,0.5),(0.9,0.5),(0.5,0.65),
            (0.5,0.85)
        ],

        "1-4-5-1": [
            (0.5,0.1),
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),
            (0.1,0.5),(0.3,0.5),(0.5,0.5),(0.7,0.5),(0.9,0.5),
            (0.5,0.85)
        ]
    }
    
    pos_order = ["All", "GK", "DF", "MF", "FW"]  # orden fijo de posiciones
    
    # Almacena los jugadores asignados a cada posición (11 posiciones)
    lineup_defaults = {
        "lineup_sistema": lineup_sistemas[0],
        "lineup_league_filter": "All",
        "lineup_team_filter": "All",
        "lineup_pos_filter": "All",
        "lineup_players": [None]*11,
        "lineup_player_to_add": "Select",
        "lineup_matchday": 1,
        "lineup_selected_pos": None,
        
        "lineup_do_reset": False
    }
    
    for key, value in lineup_defaults.items():
        st.session_state.setdefault(key, value)
        
    if st.session_state["lineup_do_reset"]:
        for key in lineup_defaults:
            st.session_state[key] = lineup_defaults[key]
        st.session_state["lineup_do_reset"] = False
        st.rerun()

    # Imagen de cancha
    lineup_pitch_img = Image.open(ASSETSIMG / "picth_vertical.png")
    w, h = lineup_pitch_img.size

    # Layout de la página
    lineup_form_col, lineup_field_col = st.columns([1,2])

    # Formulario de asignación de jugadores
    with lineup_form_col:

        st.subheader("Assign Player")
        
        # Selector de sistema táctico 
        lineup_sistema = st.selectbox(
            "Select system",
            lineup_sistemas,
            index=lineup_sistemas.index(st.session_state.get("lineup_sistema", lineup_sistemas[0]))
        )
        st.session_state["lineup_sistema"] = lineup_sistema
        lineup_pos_coords = lineup_posiciones[lineup_sistema]
        
        # Selector de liga 
        league_options = ["All"] + sorted(lineup_df_players["stats_Comp"].unique())
        league_index = league_options.index(st.session_state.get("lineup_league_filter", "All"))
        
        lineup_league = st.selectbox(
            "League",
            league_options,
            index=league_index
        )
        st.session_state["lineup_league_filter"] = lineup_league

        # Selector de equipo filtrado por liga 
        teams = sorted(lineup_df_players[lineup_df_players["stats_Comp"]==lineup_league]["stats_Squad"].unique()) \
                if lineup_league != "All" else sorted(lineup_df_players["stats_Squad"].unique())
        
        team_options = ["All"] + teams
        
        # Evitar error si el equipo previo ya no existe en la nueva lista
        team_index = team_options.index(st.session_state["lineup_team_filter"]) \
            if st.session_state.get("lineup_team_filter") in team_options else 0
        
        lineup_team = st.selectbox(
            "Team",
            team_options,
            index=team_index
        )
        st.session_state["lineup_team_filter"] = lineup_team

        # Filtrar jugadores por liga y equipo 
        filtered_players = lineup_df_players.copy()
        if lineup_league != "All":
            filtered_players = filtered_players[filtered_players["stats_Comp"] == lineup_league]
        if lineup_team != "All":
            filtered_players = filtered_players[filtered_players["stats_Squad"] == lineup_team]

        # Selector de posición 
        available_positions = [p for p in pos_order if p in filtered_players["stats_Pos"].unique()]
        pos_options = ["All"] + available_positions
        pos_index = pos_options.index(st.session_state.get("lineup_pos_filter", "All")) \
            if st.session_state.get("lineup_pos_filter") in pos_options else 0
        
        lineup_pos = st.selectbox(
            "Position",
            pos_options,
            index=pos_index
        )
        st.session_state["lineup_pos_filter"] = lineup_pos

        if lineup_pos != "All":
            filtered_players = filtered_players[filtered_players["stats_Pos"] == lineup_pos]

        # Selector de jugador 
        players_list = ["Select"] + list(filtered_players["Player"])
        player_index = players_list.index(st.session_state["lineup_player_to_add"]) \
            if st.session_state.get("lineup_player_to_add") in players_list else 0
        
        lineup_player = st.selectbox(
            "Player",
            players_list,
            index=player_index
        )
        st.session_state["lineup_player_to_add"] = lineup_player

        # Selector de jornada 
        lineup_matchday = st.slider(
            "Gameday",
            1, 38,
            st.session_state.get("lineup_matchday", 1)
        )
        st.session_state["lineup_matchday"] = lineup_matchday

        # Selector de posición a asignar 
        lineup_pos_options = [f"Pos {i+1}" for i in range(len(lineup_pos_coords))]
        selected_pos_index = st.session_state.get("lineup_selected_pos", 0)
        
        lineup_selected_pos_label = st.selectbox(
            "Select position to assign",
            lineup_pos_options,
            index=selected_pos_index
        )
        if lineup_selected_pos_label in lineup_pos_options:
            st.session_state["lineup_selected_pos"] = lineup_pos_options.index(lineup_selected_pos_label)
        else:
            st.session_state["lineup_selected_pos"] = 0

        # Botón Asignar jugador con validación 
        if st.button("Assign players"):
            if lineup_league=="All" or lineup_team=="All" or lineup_pos=="All" or lineup_player=="Select":
                st.warning("Please select League, Team, Position, and Player before assigning.")
            else:
                st.session_state["lineup_players"][st.session_state["lineup_selected_pos"]] = lineup_player
                st.rerun()

        # Botón Guardar Lineup 
        if st.button("Save lineup"):
            filename = DATA_DIR / "lineups_register.xlsx"
            
            # Si existe, lo cargamos; si no, creamos un DataFrame vacío
            if os.path.exists(filename):
                df_save = pd.read_excel(filename, engine="openpyxl")
            else:
                df_save = pd.DataFrame()

            # Preparar los datos del lineup
            lineup_data = []
            lineup_id = str(uuid.uuid4())  # ID único para este lineup
            for i, p in enumerate(st.session_state.get("lineup_players", [])):
                if p:
                    coord = lineup_pos_coords[i]
                    lineup_data.append({
                        "Lineup_Id": lineup_id,
                        "Jornada": lineup_matchday,
                        "Sistema": lineup_sistema,
                        "Jugador": p,
                        "Posición": i + 1,
                        "Coordenada X": coord[0],
                        "Coordenada Y": coord[1],
                        "Liga": lineup_league,
                        "Equipo": lineup_team,
                        "Usuario": st.session_state.get("user", "Desconocido")
                    })

            # Concatenar con los datos existentes si hay
            if not df_save.empty:
                df_save = pd.concat([df_save, pd.DataFrame(lineup_data)], ignore_index=True)
            else:
                df_save = pd.DataFrame(lineup_data)

            # Guardar directamente en disco
            df_save.to_excel(filename, index=False, engine="openpyxl")
            st.success(f"Lineup saved with ID: {lineup_id}")

            # Preparar archivo para descargar
            with BytesIO() as output:
                df_save.to_excel(output, index=False, engine="openpyxl")
                output.seek(0)
                st.download_button(
                    "📥 Download Excel",
                    data=output,
                    file_name="lineups_register.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # Botón Reset 
        if st.button("🔄 Reset"):
            # Reiniciar todos los valores del lineup
            st.session_state["lineup_sistema"] = lineup_sistemas[0]
            st.session_state["lineup_league_filter"] = "All"
            st.session_state["lineup_team_filter"] = "All"
            st.session_state["lineup_pos_filter"] = "All"
            st.session_state["lineup_players"] = [None]*11
            st.session_state["lineup_player_to_add"] = "Select"
            st.session_state["lineup_matchday"] = 1
            st.session_state["lineup_selected_pos"] = 0  # posición por defecto
            st.rerun()
        
    with lineup_field_col:

        fig_lineup, ax_lineup = plt.subplots(figsize=(w/100, h/100))
        
        # Mostrar imagen de fondo
        ax_lineup.imshow(lineup_pitch_img)
        
        # Quitar ejes
        ax_lineup.axis('off')

        # Dibujar posiciones y jugadores
        for idx, pos in enumerate(lineup_pos_coords):
            x = pos[0]*w
            y = pos[1]*h
            
            # Dibujar círculo de posición
            color = "green" if st.session_state["lineup_players"][idx] else "red"
            ax_lineup.add_patch(plt.Circle((x,y), 25, color=color))
            
            # Número de posición dentro del círculo
            ax_lineup.text(x, y, str(idx+1), color='white', ha='center', va='center', fontsize=15, fontweight='bold')

            # Mostrar nombre del jugador debajo del círculo si está asignado
            if st.session_state["lineup_players"][idx]:
                nombre = st.session_state["lineup_players"][idx]
                palabras = nombre.split()
                lineas = [" ".join(palabras[i:i+2]) for i in range(0, len(palabras),2)]
                nombre_wrap = "\n".join(lineas)
                ax_lineup.text(x, y+50, nombre_wrap, color="black", ha='center', va='top', fontsize=18)

        # Mostrar cancha con jugadores asignados
        st.pyplot(fig_lineup)
    
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

    if st.button("⚙️ Prepare PDF"):

        # Crear figura
        fig_lineup, ax_lineup = plt.subplots(figsize=(6,9))
        ax_lineup.imshow(lineup_pitch_img)
        ax_lineup.axis("off")

        for idx, pos in enumerate(lineup_pos_coords):
            x_lineup = pos[0]*w
            y_lineup = pos[1]*h
            color_lineup = "green" if st.session_state["lineup_players"][idx] else "red"
            ax_lineup.add_patch(plt.Circle((x_lineup,y_lineup), 25, color=color_lineup))
            ax_lineup.text(x_lineup, y_lineup, str(idx+1), color='white', ha='center', va='center', fontsize=7, fontweight='bold')
            if st.session_state["lineup_players"][idx]:
                nombre_lineup = st.session_state["lineup_players"][idx]
                ax_lineup.text(x_lineup, y_lineup+50, nombre_lineup, color="black", ha='center', va='top', fontsize=7)

        # 🧠 1. Guardar imagen en memoria (NO disco)
        img_buffer_lineup = BytesIO()
        fig_lineup.savefig(img_buffer_lineup, format="png", bbox_inches='tight', dpi=150)
        plt.close(fig_lineup)
        img_buffer_lineup.seek(0)

        # Crear PDF
        pdf_lineup = FPDF()
        pdf_lineup.add_page()
        pdf_lineup.add_font("DejaVu", "", str(ASSETSFONTS / "DejaVuSans.ttf"), uni=True)
        pdf_lineup.set_font("DejaVu", "", 12)

        usuario = st.session_state.get("user","Desconocido")
        sistema = st.session_state.get("lineup_sistema","1-4-4-2")
        jornada = st.session_state.get("lineup_matchday",1)
        title = f"User: {usuario}    System: {sistema}    Matchday: {jornada}"

        pdf_lineup.cell(0, 10, title, ln=True, align="C")
        pdf_lineup.ln(5)

        # 🧠 2. FPDF NO acepta BytesIO directamente → hay que pasar por base64
        img_base64_lineup = base64.b64encode(img_buffer_lineup.read()).decode("utf-8")
        img_src_lineup = f"data:image/png;base64,{img_base64_lineup}"

        pdf_lineup.image(img_src_lineup, x_lineup=15, w=180)

        # Logo
        logo_buffer_lineup = get_watermark(alpha=10)
        pdf_lineup.image(logo_buffer_lineup, x_lineup=55, y_lineup=100, w=100)

        # 🧠 3. PDF en memoria
        pdf_bytes_lineup = pdf_lineup.output(dest="S").encode("latin-1")
        b64_pdf_lineup = base64.b64encode(pdf_bytes_lineup).decode()

        # Botón rojo
        components.html(
            f"""
            <a href="data:application/pdf_lineup;base64,{b64_pdf_lineup}" download="lineup.pdf">
                <button style="
                    padding:8px 14px;
                    font-size:14px;
                    cursor:pointer;
                    background-color:#dc2626;
                    color:white;
                    border:none;
                    border-radius:6px;">
                    📄 Export to PDF
                </button>
            </a>
            """,
            height=55
        )