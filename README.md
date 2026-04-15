# Analysis Football Players

**Analysis Football Players** es una aplicación de Streamlit diseñada para facilitar el análisis de jugadores de fútbol desde el punto de vista de una dirección deportiva. Permite centralizar las funciones principales, ofreciendo herramientas para análisis de jugadores de manera individual o grupal, optimizando la gestión de datos y la toma de decisiones.

---

## Objetivo

El objetivo de la aplicación es resolver el problema de trabajar con múltiples herramientas de manera dispersa. Con esta app, un gestor puede centralizar los datos y análisis, permitiendo que todo el equipo acceda a la misma información y comience a trabajar de forma coordinada.  

Entre las posibilidades que ofrece la app se incluyen:

- Creación de **tierlists** para evaluar jugadores de interés.  
- Generación de **onces ideales** de diferentes competiciones a lo largo de las jornadas.  
- Aplicación de **filtros de datos**, ordenamiento y creación de **rankings por estadística**.  
- Visualización de **radares comparativos** entre dos jugadores.  
- Posibilidad de solicitar la importación de **nuevas competiciones** para ampliar la base de datos.  

---

## Dependencias

La aplicación requiere Python y las siguientes librerías:  

- streamlit  
- pandas  
- fpdf2  
- requests  
- Pillow  
- matplotlib  
- plotly  
- numpy  
- openpyxl  
- LanusStats  
- IPython  
- python-dotenv  
- scipy

Se pueden instalar con:

```bash
pip install -r requirements.txt
```

---

## Cómo ejecutar la aplicación

##### Clonar el repositorio y situarse en la carpeta del proyecto:

```bash
git clone <url-del-repo>
cd Tarea_M8_ZIP
```

##### Instalar las dependencias:

```bash
pip install -r requirements.txt
```

##### Ejecutar la aplicación con Streamlit:

```bash
streamlit run app.py
```

##### Abrir la URL que muestra Streamlit en el navegador para acceder a la app.

---

## Funcionalidades principales

**Gestión de usuarios:** Control de acceso a la aplicación y permisos.

**Lineups:** Crear y analizar alineaciones de equipos con posiciones, sistemas de juego y coordenadas.

**Listas de jugadores:** Filtrar, evaluar y organizar jugadores según observaciones y proyecciones.

**Rankings y filtros:** Ordenar jugadores por estadísticas y crear rankings personalizados.

**Radares comparativos:** Comparar visualmente el rendimiento de dos jugadores.

**Once ideal:** Generar alineaciones ideales de diferentes competiciones a lo largo de las jornadas.

**Solicitud de nuevas competiciones:** Los usuarios pueden enviar sugerencias para importar competiciones nuevas desde Fbref.

---

## Notas adicionales

Los datos provienen de **Fbref** y han sido obtenidos mediante **LanusStats.**

Todos los datos están precargados y disponibles en la carpeta <code>data/</code>.

El archivo <code>README_DATA.md</code> dentro de la carpeta <code>data/</code> explica en detalle el contenido de cada archivo de datos.

Para la visualización de campos y alineaciones se han utilizado las librerías de mplsoccer y Python.