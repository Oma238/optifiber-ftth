"""Pruebas de integracion de los repositorios de OptiFiber."""

import pytest
from sqlalchemy import func, select

from src.dominio.servicios import ErrorDominio
from src.infraestructura.modelos import (
    CategoriaModel,
    ClienteModel,
    DetallePedidoModel,
    EtiquetaModel,
    PedidoModel,
    ProductoModel,
)
from src.infraestructura.repositorios import (
    CatalogoRepositorio,
    ClienteRepositorio,
    PedidoRepositorio,
)


@pytest.fixture
def datos_base(db_session):
    categoria = CategoriaModel(nombre="Equipos ONT/ONU")
    producto = ProductoModel(
        sku="ONT-001",
        nombre="ONT GPON WiFi 5",
        precio=220.0,
        stock=10,
        categoria=categoria,
    )
    cliente = ClienteModel(
        nombre="Ana Quispe",
        documento="12345678",
        telefono="987654321",
    )
    db_session.add_all([categoria, producto, cliente])
    db_session.commit()
    return {"categoria": categoria, "producto": producto, "cliente": cliente}


def test_crear_pedido_descuenta_stock_y_calcula_total(db_session, datos_base):
    repositorio = PedidoRepositorio(db_session)

    pedido = repositorio.crear_pedido("12345678", [("ONT-001", 2)])

    assert pedido.total == 440.0
    assert len(pedido.detalles) == 1
    assert pedido.detalles[0].cantidad == 2
    assert pedido.detalles[0].subtotal == 440.0
    assert db_session.get(ProductoModel, datos_base["producto"].id).stock == 8
    assert len(datos_base["cliente"].pedidos) == 1


def test_crear_pedido_aplica_descuento_por_volumen(db_session, datos_base):
    producto = ProductoModel(
        sku="FIB-002",
        nombre="Cable ADSS 12 hilos",
        precio=890.0,
        stock=5,
        categoria=datos_base["categoria"],
    )
    db_session.add(producto)
    db_session.commit()

    pedido = PedidoRepositorio(db_session).crear_pedido("12345678", [("FIB-002", 2)])

    assert pedido.total == 1691.0


def test_crear_pedido_rechaza_stock_insuficiente(db_session, datos_base):
    repositorio = PedidoRepositorio(db_session)

    with pytest.raises(ErrorDominio, match="Stock insuficiente"):
        repositorio.crear_pedido("12345678", [("ONT-001", 99)])

    db_session.expire_all()
    producto_db = db_session.get(ProductoModel, datos_base["producto"].id)
    assert producto_db.stock == 10
    assert db_session.scalar(select(func.count(DetallePedidoModel.id))) == 0


def test_cliente_rechaza_documento_duplicado(db_session, datos_base):
    with pytest.raises(ErrorDominio, match="Ya existe un cliente"):
        ClienteRepositorio(db_session).crear("Otra Persona", "12345678")


def test_eliminar_cliente_aplica_cascada_a_pedidos(db_session, datos_base):
    pedido = PedidoRepositorio(db_session).crear_pedido("12345678", [("ONT-001", 1)])
    pedido_id = pedido.id

    eliminado = ClienteRepositorio(db_session).eliminar(datos_base["cliente"].id)

    assert eliminado is True
    assert db_session.get(PedidoModel, pedido_id) is None
    assert db_session.scalar(select(func.count(DetallePedidoModel.id))) == 0


def test_catalogo_lista_productos_con_categoria_y_etiquetas(db_session, datos_base):
    producto = db_session.get(ProductoModel, datos_base["producto"].id)
    producto.etiquetas.append(EtiquetaModel(nombre="hogar"))
    db_session.commit()

    productos = CatalogoRepositorio(db_session).listar_productos()

    assert len(productos) == 1
    assert productos[0].categoria.nombre == "Equipos ONT/ONU"
    assert productos[0].etiquetas[0].nombre == "hogar"
    assert productos[0].sku == "ONT-001"
