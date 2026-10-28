"""Pruebas unitarias de las reglas de negocio puras de OptiFiber."""

import pytest

from src.dominio.servicios import (
    ErrorDominio,
    calcular_descuento,
    calcular_subtotal,
    calcular_total_pedido,
    validar_cantidad,
    validar_documento,
    validar_stock,
)


def test_calcular_subtotal_redondea_a_dos_decimales():
    assert calcular_subtotal(3, 4.567) == 13.7
    assert calcular_subtotal(2, 85.0) == 170.0


def test_calcular_total_sin_descuento_bajo_el_umbral():
    assert calcular_total_pedido([(2, 220.0), (1, 18.0)]) == 458.0
    assert calcular_descuento(458.0) == 0.0


def test_calcular_total_aplica_descuento_por_volumen():
    # 2 x 890 = 1780; 5% de descuento = 89; total = 1691
    assert calcular_descuento(1780.0) == 89.0
    assert calcular_total_pedido([(2, 890.0)]) == 1691.0


def test_validar_stock_rechaza_cantidad_insuficiente():
    with pytest.raises(ErrorDominio, match="Stock insuficiente"):
        validar_stock(11, 10)


def test_validar_cantidad_rechaza_cero_y_negativos():
    with pytest.raises(ErrorDominio):
        validar_cantidad(0)
    with pytest.raises(ErrorDominio):
        validar_cantidad(-3)


def test_validar_documento_acepta_dni_y_ruc():
    assert validar_documento(" 12345678 ") == "12345678"
    assert validar_documento("20512345678") == "20512345678"


@pytest.mark.parametrize("documento", ["", "123", "1234567A", "123456789"])
def test_validar_documento_rechaza_formatos_invalidos(documento):
    with pytest.raises(ErrorDominio):
        validar_documento(documento)
