# ============================================
# Page New League Request
# ============================================

# Importar librerías
import streamlit as st
import pandas as pd
import os
from PIL import Image
from datetime import datetime

# Importar funciones de datos
from controllers.db_controller import load_stats_players_fbref

# Importar rutas de configuración
from common.config import (
    ASSETSIMG, DATA_DIR
)

# Función que da como resultado la página New League
def page_newleague():

    # Se crean 3 columnas para centrar la imagen
    newleague_imgcol1, newleague_imgcol2, newleague_imgcol3 = st.columns([3,2,3])

    with newleague_imgcol2:

        # Se carga una imagen desde la carpeta assets
        header_img = Image.open(ASSETSIMG / "Freepick NewLeague.png")

        # Se muestra la imagen en Streamlit
        st.image(header_img, width=120)

    # Título de la página
    st.header("Request a New Competition")

    st.caption("Suggest a new league to be added to the scouting database")

    st.markdown("---")

    # Archivo donde se guardan las peticiones
    MESSAGE_FILE = DATA_DIR / "message_from_users.xlsx"

    # Función auxiliar para cargar mensajes existentes
    def load_messages():

        # Definir las columnas que esperamos en el Excel
        columns = ["User","League","Priority","Message","Date"]

        # Si el archivo no existe, devolver un DataFrame vacío con las columnas definidas
        if not os.path.exists(MESSAGE_FILE):
            return pd.DataFrame(columns=columns)

        # Si el archivo existe, se lee y devuelve como DataFrame
        return pd.read_excel(MESSAGE_FILE)

    # Función auxiliar para guardar mensaje
    def save_message(data):
        
        # Convertir el diccionario 'data' en un DataFrame de una sola fila
        df_new = pd.DataFrame([data])

        # Si el archivo no existe, se crea y escribe la fila nueva
        if not os.path.exists(MESSAGE_FILE):
            with pd.ExcelWriter(MESSAGE_FILE, engine="openpyxl") as writer:
                df_new.to_excel(writer, index=False)  

        # Si el archivo ya existe, se carga y agrega la nueva fila
        else:
            # Leer el Excel existente
            df_old = pd.read_excel(MESSAGE_FILE)

            # Concatenar los datos antiguos con los nuevos, ignorando los índices antiguos
            df_final = pd.concat([df_old, df_new], ignore_index=True)

            # Guardar de nuevo todo el DataFrame en el mismo archivo (sobrescribiendo)
            with pd.ExcelWriter(MESSAGE_FILE, engine="openpyxl", mode="w") as writer:
                df_final.to_excel(writer, index=False)

    # Función que devuelve un diccionario con todas las ligas posibles para distintas fuentes
    @st.cache_data(show_spinner=False)
    def load_leagues():
        
        # Lista fija de ligas
        lista_ligas = [
            "Copa de la Liga",
            "Primera Division Argentina",
            "Primera Division Uruguay",
            "Brasileirao",
            "Brasileirao B",
            "Primera Division Colombia",
            "Primera Division Chile",
            "Primera Division Peru",
            "Primera Division Venezuela",
            "Primera Division Ecuador",
            "Primera Division Bolivia",
            "Primera Division Paraguay",
            "Brasileirao F",
            "MLS",
            "USL Championship",
            "Premier League",
            "La Liga",
            "Ligue 1",
            "Bundesliga",
            "Serie A",
            "Big 5 European Leagues",
            "Danish Superliga",
            "Eredivisie",
            "Primeira Liga Portugal",
            "Copa America",
            "Euros",
            "Saudi League",
            "EFL Championship",
            "La Liga 2",
            "Belgian Pro League",
            "Challenger Pro League",
            "2. Bundesliga",
            "Ligue 2",
            "Serie B",
            "J1 League",
            "NWSL",
            "Womens Super League",
            "Liga F",
            "Premier Division South Africa",
            "Champions League",
            "Europa League",
            "Conference League",
            "Copa Libertadores",
            "Liga MX"
        ]
        # Devolver dict con la misma estructura que LanusStats esperaba
        return {"Fbref": {liga: {} for liga in lista_ligas}}
        
    ligas = load_leagues()

    # Filtrar solo las ligas de FBref
    ligas_fbref = ligas["Fbref"]

    # Obtener una lista ordenada con los nombres de las competiciones
    lista_ligas = sorted(list(ligas_fbref.keys()))

    # Cargar el df con los datos de Fbref
    newleague_df_players = load_stats_players_fbref()  
    
    # Supongamos que df["stats_Comp"] contiene valores con posibles comas
    existing_comps = newleague_df_players["stats_Comp"].apply(lambda x: str(x).split(",")[0].strip())

    # Valores únicos y ordenados
    existing_comps = sorted(existing_comps.unique())

    # Filtrar lista de ligas posibles para que no incluya las que ya están en la DB
    lista_ligas_filtrada = [l for l in lista_ligas if l not in existing_comps]
    
    # Layout de la página
    newleague_form_col, newleague_info_col = st.columns([1,1])

    # Columna del formulario para enviar solicitud de nueva liga
    with newleague_form_col:

        st.subheader("Submit Request")

        # Selector desplegable de competiciones disponibles
        selected_league = st.selectbox(
            "Select Competition",
            ["Select"] + lista_ligas_filtrada,  # Solo ligas no presentes
            key="new_league_select"
        )

        # Radio para seleccionar el nivel de prioridad del mensaje
        priority = st.radio(
            "Priority Level",
            ["Low","Medium","High"],
            key="league_priority"
        )

        # Área de texto para que el usuario justifique por qué quiere la liga
        message = st.text_area(
            "Why should this league be added?",
            max_chars=300,
            placeholder="Explain why this competition would be useful for scouting...",
            key="league_message"
        )

        # Botón para enviar la solicitud
        if st.button("Send Request"):
            
            # Validación: debe seleccionar una competición
            if selected_league == "Select":
                st.warning("Please select a competition")

            # Validación: debe escribir un mensaje
            elif not message:
                st.warning("Please write a justification")

            # Si todo es correcto, crear el diccionario con la información del mensaje
            else:
                data = {
                    "User": st.session_state.get("user"),  # Usuario que envía el mensaje
                    "League": selected_league,            # Liga solicitada
                    "Priority": priority,                 # Nivel de prioridad
                    "Message": message,                   # Justificación
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M")  # Fecha y hora actual
                }

                # Guardar el mensaje en el Excel correspondiente
                save_message(data)

                # Confirmación visual al usuario
                st.success("Your request has been sent to the administrator")

                # Recargar la app para limpiar inputs
                st.rerun()

    # Columna de información: mostrar competiciones y estadísticas 
    with newleague_info_col:

        st.subheader("Available Competitions")

        # Info rápida: cuántas competiciones hay disponibles en FBref
        st.info(f"Total competitions available in FBref: {len(lista_ligas)}")

        # Expander para listar todas las competiciones
        with st.expander("View all competitions"):

            # Iterar sobre todas las competiciones y mostrarlas
            for league in lista_ligas:
                st.write("ℹ", league)  # Icono de información delante del nombre
        
        with st.expander("View competitions in app"):

            # Mostrar competiciones únicas ya presentes en la base de datos
            if existing_comps:
                for comp in existing_comps:
                    st.write("✅", comp)
            else:
                st.write("No competitions in the app yet")

        st.markdown("---")

        # Cargar mensajes existentes de usuarios
        df_messages = load_messages()

        # Si hay mensajes, mostrar estadísticas de las ligas más solicitadas
        if not df_messages.empty:

            st.subheader("Most Requested Leagues")

            # Contar cuántas veces se ha solicitado cada liga
            league_counts = (
                df_messages["League"]
                .value_counts()
                .reset_index()
            )

            # Renombrar columnas para claridad
            league_counts.columns = ["League","Requests"]

            # Mostrar las 5 ligas más solicitadas en un dataframe
            st.dataframe(
                league_counts.head(5),
                use_container_width=True
            )

        # Si no hay mensajes aún, mostrar un mensaje informativo
        else:
            st.caption("No league requests yet")
