"""Funciones de formato y colores semanticos compartidos por la interfaz."""

from __future__ import annotations

from datetime import date

from src.presentacion.gui.tema import (
    ALERTA,
    ALERTA_FONDO,
    EXITO,
    EXITO_FONDO,
    INFO,
    INFO_FONDO,
    PELIGRO,
    PELIGRO_FONDO,
    TEXTO_SUAVE,
)

MESES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)

DIAS = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")

SUFIJOS_EMPRESA = {"SAC", "SA", "EIRL", "SRL"}

COLORES_ESTADO = {
    "PENDIENTE": (ALERTA, ALERTA_FONDO),
    "PAGADO": (EXITO, EXITO_FONDO),
    "ENVIADO": (INFO, INFO_FONDO),
    "CANCELADO": (PELIGRO, PELIGRO_FONDO),
}


def formato_moneda(valor: float) -> str:
    """Formatea un monto en soles con separador de miles."""
    return f"S/ {valor:,.2f}"


def formato_fecha(valor: date | None) -> str:
    """Devuelve una fecha corta en formato peruano."""
    if valor is None:
        return "-"
    return valor.strftime("%d/%m/%Y")


def fecha_larga(valor: date | None = None) -> str:
    """Devuelve una fecha legible para la barra superior."""
    valor = valor or date.today()
    return f"{DIAS[valor.weekday()]}, {valor.day} de {MESES[valor.month - 1]} de {valor.year}"


def truncar(texto: object, ancho: int) -> str:
    """Recorta un texto con puntos suspensivos sin romper el layout."""
    limpio = str(texto)
    if len(limpio) <= ancho:
        return limpio
    return f"{limpio[: ancho - 1].rstrip()}…"


def iniciales(nombre: str) -> str:
    """Obtiene hasta dos iniciales para el avatar del cliente."""
    partes = [
        parte
        for parte in nombre.replace(".", " ").split()
        if parte and parte.upper() not in SUFIJOS_EMPRESA
    ]
    if not partes:
        partes = [parte for parte in nombre.split() if parte]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return f"{partes[0][0]}{partes[-1][0]}".upper()


def colores_estado(estado: str) -> tuple[str, str]:
    """Devuelve (color de texto, color de fondo) para un estado de pedido."""
    return COLORES_ESTADO.get(estado.upper(), (TEXTO_SUAVE, "#161F2A"))


def colores_stock(stock: int) -> tuple[str, str]:
    """Semantica visual del inventario: critico, bajo o saludable."""
    if stock <= 0:
        return PELIGRO, PELIGRO_FONDO
    if stock <= 5:
        return PELIGRO, PELIGRO_FONDO
    if stock <= 10:
        return ALERTA, ALERTA_FONDO
    return EXITO, EXITO_FONDO
