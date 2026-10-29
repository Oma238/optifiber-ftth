"""Pruebas de los datos iniciales y de los pedidos de demostracion."""

from sqlalchemy import func, select

from src.infraestructura.modelos import PedidoModel, ProductoModel
from src.infraestructura.seed import sembrar_datos, sembrar_pedidos_demo


def test_sembrar_datos_carga_catalogo_y_clientes(db_session):
    sembrar_datos(db_session)

    assert db_session.scalar(select(func.count(ProductoModel.id))) == 10
    assert db_session.scalar(select(func.count(PedidoModel.id))) == 0

    # Una segunda llamada no debe duplicar el catalogo.
    sembrar_datos(db_session)
    assert db_session.scalar(select(func.count(ProductoModel.id))) == 10


def test_sembrar_pedidos_demo_es_idempotente_y_descuenta_stock(db_session):
    sembrar_datos(db_session)
    stock_inicial = db_session.scalar(
        select(ProductoModel.stock).where(ProductoModel.sku == "FIB-001")
    )

    sembrar_pedidos_demo(db_session)
    total_pedidos = db_session.scalar(select(func.count(PedidoModel.id)))
    assert total_pedidos == 5

    stock_final = db_session.scalar(
        select(ProductoModel.stock).where(ProductoModel.sku == "FIB-001")
    )
    assert stock_final == stock_inicial - 2

    # La firma cliente/estado/lineas evita duplicados en arranques posteriores.
    sembrar_pedidos_demo(db_session)
    assert db_session.scalar(select(func.count(PedidoModel.id))) == total_pedidos
