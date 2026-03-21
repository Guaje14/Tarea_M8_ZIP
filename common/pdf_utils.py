# ============================================
# Common -> pdf_utils
# ============================================

# Importar librerías
import tempfile
from PIL import Image

# Importar rutas de configuración
from common.config import (
    ASSETSIMG
)

# Función para crear la marca de agua
def get_watermark(alpha: int = 30, logo_filename: str = "Logo_app_StreamlitM8.png") -> str:

    # Abrir logo y convertir a RGBA
    watermark = Image.open(ASSETSIMG / logo_filename).convert("RGBA")
    
    # Aplicar transparencia
    watermark.putalpha(alpha)
    
    # Guardar en buffer
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    watermark.save(tmp_file.name, format="PNG")
    tmp_file.close()
    
    return tmp_file.name