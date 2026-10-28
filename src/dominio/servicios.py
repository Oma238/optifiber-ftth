"""Servicios de dominio de OptiFiber.

Estas funciones no conocen SQLAlchemy ni la base de datos: reciben datos y
devuelven resultados. Asi se mantiene la separacion de capas exigida por el
instructivo.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal

CENTIMOS = Decimal("0.01")
UMBRAL_DESCUENTO = Decimal("1500.00")
PORCENTAJE_DESCUENTO = Decimal("0.05")


class ErrorDominio(ValueError):
    """Error controlado de una regla de negocio."""


def _a_decimal(valor: float | int | Decimal) -> Decimal:
    """Convierte un numero a Decimal sin arrastrar errores de punto flotante."""
    return Decimal(str(valor))


def _redondear(valor: Decimal) -> Decimal:
    return valor.quantize(CENTIMOS, rounding=ROUND_HALF_UP)


def calcular_subtotal(cantidad: int, precio_unitario: float) -> float:
    """Calcula el subtotal de una linea y lo redondea a dos decimales."""
    if cantidad <= 0:
        raise ErrorDominio("La cantidad debe ser mayor que cero.")
    if precio_unitario < 0:
        raise ErrorDominio("El precio unitario no puede ser negativo.")

    subtotal = _a_decimal(cantidad) * _a_decimal(precio_unitario)
    return float(_redondear(subtotal))


def calcular_descuento(total_sin_descuento: float) -> float:
    """Devuelve el monto del descuento por volumen (5% desde S/ 1500)."""
    total = _a_decimal(total_sin_descuento)
    if total < UMBRAL_DESCUENTO:
        return 0.0
    return float(_redondear(total * PORCENTAJE_DESCUENTO))


def calcular_total_pedido(lineas: Iterable[tuple[int, float]]) -> float:
    """Suma las lineas y aplica el descuento por volumen si corresponde.

    ``lineas`` contiene tuplas ``(cantidad, precio_unitario)``.
    """
    total = Decimal("0.00")
    for cantidad, precio_unitario in lineas:
        total += _a_decimal(calcular_subtotal(cantidad, precio_unitario))

    descuento = _a_decimal(calcular_descuento(float(total)))
    return float(_redondear(total - descuento))


def validar_stock(cantidad: int, stock_disponible: int) -> None:
    """Valida que exista stock suficiente para la cantidad solicitada."""
    if cantidad <= 0:
        raise ErrorDominio("La cantidad debe ser mayor que cero.")
    if cantidad > stock_disponible:
        raise ErrorDominio(
            f"Stock insuficiente: se solicitan {cantidad} unidades y solo hay "
            f"{stock_disponible} disponibles."
        )


def validar_documento(documento: str) -> str:
    """Normaliza y valida un DNI (8 digitos) o RUC (11 digitos)."""
    limpio = documento.strip()
    if not limpio:
        raise ErrorDominio("El documento del cliente es obligatorio.")
    if not limpio.isdigit():
        raise ErrorDominio("El documento solo debe contener digitos.")
    if len(limpio) not in {8, 11}:
        raise ErrorDominio("El documento debe tener 8 digitos (DNI) u 11 digitos (RUC).")
    return limpio


def validar_cantidad(cantidad: int) -> int:
    """Valida una cantidad positiva proveniente de la interfaz."""
    if cantidad <= 0:
        raise ErrorDominio("La cantidad debe ser mayor que cero.")
    return cantidad
