# ============================================
# Common -> pdf_utils
# ============================================

# Importar librerías
import tempfile
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

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

# Función para generar un radar según el tipo y método seleccionado
def generate_radar_matplotlib(rA_vals, rB_vals, selected_stats, playerA, playerB, chart_type_val, textA, textB):

    # Número de estadísticas a graficar
    n = len(selected_stats)  

    # Calcular ángulos para cada estadística en el radar 
    angles = np.linspace(0, 2*np.pi, n, endpoint=False).tolist()  
    angles += angles[:1]  

    # Preparar valores para plot 
    rA_plot = rA_vals + rA_vals[:1]
    rB_plot = rB_vals + rB_vals[:1]

    # Crear figura y eje polar 
    fig, ax = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True))

    if chart_type_val == "Compare Players":
        
        # Jugador A
        ax.plot(angles, rA_plot, color="#1f77b4", linewidth=2, label=playerA)
        ax.fill(angles, rA_plot, color="#1f77b4", alpha=0.25)  # Relleno semi-transparente

        # Jugador B
        ax.plot(angles, rB_plot, color="#d62728", linewidth=2, label=playerB)
        ax.fill(angles, rB_plot, color="#d62728", alpha=0.25)
        
        if textA and textB:
            for i in range(n):
                angle = angles[i]

                ax.text(angle, rA_vals[i] + 5, textA[i],
                        color="#1f77b4", fontsize=9, ha="center", va="center")

                ax.text(angle, rB_vals[i] + 10, textB[i],
                        color="#d62728", fontsize=9, ha="center", va="center")

    elif chart_type_val == "The Best Player":
        
        plotted_players = set()
        
        for i in range(n):
            
            # Determinar cuál jugador tiene mejor valor
            if rA_vals[i] >= rB_vals[i]:
                val = rA_vals[i]
                color = "#1f77b4"
                name = playerA
                text = textA[i] if textA else ""
            else:
                val = rB_vals[i]
                color = "#d62728"
                name = playerB
                text = textB[i] if textB else ""
            
            label = name if name not in plotted_players else None
            plotted_players.add(name)

            ax.plot([angles[i], angles[i]], [0, val],
                    color=color, linewidth=4, label=label)

            ax.text(angles[i], val + 5, text,
                    color="black", fontsize=9,
                    ha="center", va="center")

    # Configurar etiquetas y ticks 
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(selected_stats, fontsize=10)

    ax.set_yticks(range(0, 101, 20))
    ax.set_ylim(0, 100)

    ax.grid(True)

    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.15),
        ncol=2,
        frameon=False
    )

    return fig
