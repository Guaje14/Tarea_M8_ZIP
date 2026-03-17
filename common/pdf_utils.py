# ============================================
# Common -> pdf_utils
# ============================================

# Importar librerías
from io import BytesIO
from PIL import Image

# Importar rutas de configuración
from common.config import (
    ASSETSIMG
)

# Función para crear la marca de agua
def get_watermark(alpha: int = 30, logo_filename: str = "Logo_app_StreamlitM8.png") -> BytesIO:

    # Abrir logo y convertir a RGBA
    watermark = Image.open(ASSETSIMG / logo_filename).convert("RGBA")
    
    # Aplicar transparencia
    watermark.putalpha(alpha)
    
    # Guardar en buffer
    buffer = BytesIO()
    watermark.save(buffer, format="PNG")
    buffer.seek(0)
    
    return buffer