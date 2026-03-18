# ============================================
# Common -> config
# ============================================

# Importar librerías 
from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

# Raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent  

# Path Img
ASSETSIMG = BASE_DIR / "assets" / "img"

# Ruta a la carpeta de fuentes
ASSETSFONTS = BASE_DIR / "assets" / "font"

# Path Data
DATA_DIR = BASE_DIR / "data"

# Path importados de env
DB_PATH = BASE_DIR / os.getenv("DB_PATH")
ACCESS_LOG = BASE_DIR / os.getenv("ACCESS_LOG")
USERS_FILE = BASE_DIR / os.getenv("USERS_FILE")
LOG_FILE = BASE_DIR / os.getenv("LOG_FILE")
