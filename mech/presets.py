"""Presets de calidad. Región 3D renderizada (el resto del lienzo 1080x1920 se compone en 2D)."""
PRESETS = {
    # nombre: (ancho 3D, alto 3D, fps, muestras Cycles, escala del lienzo final)
    "draft": dict(w=486, h=513, fps=12, samples=8, canvas=(540, 960)),
    "still": dict(w=756, h=798, fps=12, samples=14, canvas=(756, 1344)),
    "final": dict(w=864, h=912, fps=30, out_fps=60, samples=4, bounces=4, canvas=(1080, 1920)),
}
# La región 3D se coloca en el lienzo en y = REGION_Y (px del lienzo 1080x1920, se reescala por preset).
REGION_Y = 330
