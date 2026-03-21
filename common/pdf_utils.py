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

    # Número de estadísticas a mostrar
    n = len(selected_stats)

    # Ángulos para cada estadística en el radar (circular)
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)

    # Ancho de cada barra en el radar (90% del espacio disponible)
    width = (2*np.pi / n) * 0.9

    # Crear figura y eje polar
    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))

    # Si el tipo de gráfico es comparar jugadores
    if chart_type_val == "Compare Players":
        
        for i in range(n):
            
            # Dibujar barra para el jugador A
            ax.bar(
                angles[i],
                rA_vals[i],
                width=width,
                color="#1f77b4",
                alpha=0.6
            )

            # Dibujar barra para el jugador B
            ax.bar(
                angles[i],
                rB_vals[i],
                width=width,
                color="#d62728",
                alpha=0.6
            )

            # Añadir etiquetas para el jugador A
            ax.text(
                angles[i],
                rA_vals[i] + 5,
                textA[i],
                color="#1f77b4",
                fontsize=9,
                ha="center"
            )

            # Añadir etiquetas para el jugador B
            ax.text(
                angles[i],
                rB_vals[i] + 10,
                textB[i],
                color="#d62728",
                fontsize=9,
                ha="center"
            )

        # Leyenda dummy para colores de jugadores
        ax.bar(0, 0, color="#1f77b4", label=playerA)
        ax.bar(0, 0, color="#d62728", label=playerB)

    # Si el tipo de gráfico es "El mejor jugador" (selecciona solo la mejor barra)
    elif chart_type_val == "The Best Player":
        
        # Llevar registro de jugadores ya etiquetados
        plotted = set() 

        for i in range(n):
            
            # Seleccionar la mayor estadística
            if rA_vals[i] >= rB_vals[i]:
                val = rA_vals[i]
                color = "#1f77b4"
                name = playerA
                text = textA[i]
            else:
                val = rB_vals[i]
                color = "#d62728"
                name = playerB
                text = textB[i]

            # Añadir etiqueta solo una vez por jugador
            label = name if name not in plotted else None
            plotted.add(name)

            # Dibujar barra
            ax.bar(
                angles[i],
                val,
                width=width,
                color=color,
                alpha=0.8,
                label=label
            )

            # Añadir texto sobre la barra
            ax.text(
                angles[i],
                val + 5,
                text,
                color="black",
                fontsize=9,
                ha="center"
            )

    # Configuración de etiquetas de las estadísticas
    ax.set_xticks(angles)
    ax.set_xticklabels(selected_stats, fontsize=10)
    ax.tick_params(axis='x', pad=20)

    # Configuración de eje radial
    ax.set_yticks(range(0, 101, 20))    # Ticks cada 20 unidades
    ax.set_ylim(0, 100)                 # Límite del radar
    ax.grid(True)                       # Mostrar cuadrícula

    # Leyenda centrada arriba
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.15),
        ncol=2,
        frameon=False
    )

    # Devolver la figura generada
    return fig