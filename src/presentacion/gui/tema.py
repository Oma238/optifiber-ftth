"""Paleta, tipografias y medidas de la interfaz grafica de OptiFiber."""

from __future__ import annotations

# Fondos
FONDO = "#070B10"
FONDO_ALT = "#090E14"
BARRA_LATERAL = "#0A0F16"
PANEL = "#0E151E"
PANEL_ALT = "#111925"
PANEL_HOVER = "#16202C"

# Bordes y textos
BORDE = "#1C2633"
BORDE_SUAVE = "#151D27"
TEXTO = "#F4F7FB"
TEXTO_MEDIO = "#A9B6C6"
TEXTO_SUAVE = "#7D8B9D"
TEXTO_TENUE = "#566576"

# Acento principal: turquesa optico
ACENTO = "#2DD4BF"
ACENTO_HOVER = "#5EEAD4"
ACENTO_PRESIONADO = "#14B8A6"
ACENTO_TEXTO = "#032A25"
ACENTO_FONDO = "#0C2A27"

# Colores semanticos
EXITO = "#34D399"
EXITO_FONDO = "#0C2A22"
ALERTA = "#FBBF24"
ALERTA_FONDO = "#2A2110"
PELIGRO = "#F87171"
PELIGRO_FONDO = "#2A1417"
INFO = "#60A5FA"
INFO_FONDO = "#12213A"
MORADO = "#A78BFA"
MORADO_FONDO = "#1E1A33"

# Radios
RADIO_TARJETA = 16
RADIO_CONTROL = 10
RADIO_PILDORA = 7


def fuente(tamano: int = 13, negrita: bool = False, familia: str = "Segoe UI") -> tuple:
    """Devuelve una tupla de fuente compatible con Tkinter."""
    return (familia, tamano, "bold" if negrita else "normal")


def mono(tamano: int = 12, negrita: bool = False) -> tuple:
    """Fuente monoespaciada para cifras, SKU y documentos."""
    return ("Consolas", tamano, "bold" if negrita else "normal")
