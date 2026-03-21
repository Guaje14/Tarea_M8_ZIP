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
def generate_radar_matplotlib(
    rA_vals, rB_vals, selected_stats,
    playerA, playerB,
    chart_type_val,
    textA, textB
):


    n = len(selected_stats)

    # Ángulos
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)

    # Ancho de cada porción
    width = (2*np.pi / n) * 0.9

    fig, ax = plt.subplots(figsize=(3,3), subplot_kw=dict(polar=True))

    # =========================
    # COMPARE PLAYERS (PIZZA)
    # =========================
    if chart_type_val == "Compare Players":

        for i in range(n):

            # Jugador A
            ax.bar(
                angles[i],
                rA_vals[i],
                width=width,
                color="#1f77b4",
                alpha=0.6
            )

            # Jugador B (encima)
            ax.bar(
                angles[i],
                rB_vals[i],
                width=width,
                color="#d62728",
                alpha=0.6
            )

            # TEXTOS
            ax.text(
                angles[i],
                rA_vals[i] + 5,
                textA[i],
                color="#1f77b4",
                fontsize=9,
                ha="center"
            )

            ax.text(
                angles[i],
                rB_vals[i] + 10,
                textB[i],
                color="#d62728",
                fontsize=9,
                ha="center"
            )

        # Leyenda manual (porque bar no la maneja bien)
        ax.bar(0, 0, color="#1f77b4", label=playerA)
        ax.bar(0, 0, color="#d62728", label=playerB)

    # =========================
    # BEST PLAYER (PIZZA)
    # =========================
    elif chart_type_val == "The Best Player":

        plotted = set()

        for i in range(n):

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

            label = name if name not in plotted else None
            plotted.add(name)

            ax.bar(
                angles[i],
                val,
                width=width,
                color=color,
                alpha=0.8,
                label=label
            )

            ax.text(
                angles[i],
                val + 5,
                text,
                color="black",
                fontsize=9,
                ha="center"
            )

    # =========================
    # ESTILO
    # =========================
    ax.set_xticks(angles)
    ax.set_xticklabels(selected_stats, fontsize=10)

    ax.set_yticks(range(0, 101, 20))
    ax.set_ylim(0, 100)

    ax.grid(True)

    # Leyenda tipo Plotly
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.15),
        ncol=2,
        frameon=False
    )

    return fig