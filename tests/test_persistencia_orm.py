"""Pruebas de persistencia ORM del PBI-02 de OptiFiber.

Cubren la relacion 1:N Cliente-Pedido, la eliminacion en cascada, la relacion
N:M Producto-Etiqueta y la cascada Pedido-DetallePedido.
"""

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from src.infraestructura.modelos import (
    CategoriaModel,
    ClienteModel,
    DetallePedidoModel,
    EtiquetaModel,
    PedidoModel,
    ProductoModel,
)


def test_guardar_cliente_con_sus_pedidos(db_session):
    # Dado un cliente con dos pedidos asociados
    cliente = ClienteModel(
        nombre="Ana Quispe",
        documento="12345678",
        telefono="987654321",
        email="ana.quispe@example.com",
    )
    PedidoModel(total=2500.0, cliente=cliente)
    PedidoModel(total=50.0, cliente=cliente)

    # Cuando se persiste en la base de datos
    db_session.add(cliente)
    db_session.commit()

    # Entonces se consulta y se recupera con sus relaciones
    stmt = select(ClienteModel).filter_by(nombre="Ana Quispe")
    cliente_db = db_session.scalars(stmt).first()
    assert cliente_db is not None
    assert len(cliente_db.pedidos) == 2
    assert cliente_db.pedidos[0].cliente.nombre == "Ana Quispe"


def test_eliminar_cliente_elimina_sus_pedidos(db_session):
    # Dado un cliente con un pedido persistido
    cliente = ClienteModel(nombre="Luis Ramos", documento="87654321")
    PedidoModel(total=120.0, cliente=cliente)
    db_session.add(cliente)
    db_session.commit()
    cliente_id = cliente.id

    # Cuando se elimina el cliente
    db_session.delete(cliente)
    db_session.commit()

    # Entonces sus pedidos tambien desaparecen de la base de datos
    pedido_db = db_session.scalars(
        select(PedidoModel).where(PedidoModel.cliente_id == cliente_id)
    ).first()
    assert pedido_db is None


def test_relacion_nm_producto_etiqueta(db_session):
    # Dado un producto con dos etiquetas
    categoria = CategoriaModel(nombre="Equipos ONT/ONU")
    hogar = EtiquetaModel(nombre="hogar")
    empresa = EtiquetaModel(nombre="empresa")
    producto = ProductoModel(
        sku="ONT-001",
        nombre="ONT GPON WiFi 5 dual band",
        precio=220.0,
        stock=25,
        categoria=categoria,
        etiquetas=[hogar, empresa],
    )
    db_session.add(producto)
    db_session.commit()

    # Cuando se consulta el producto
    producto_db = db_session.scalars(
        select(ProductoModel).where(ProductoModel.sku == "ONT-001")
    ).first()

    # Entonces se recuperan sus etiquetas y la navegacion inversa N:M
    assert producto_db is not None
    assert {etiqueta.nombre for etiqueta in producto_db.etiquetas} == {"hogar", "empresa"}
    assert all(
        p.sku == "ONT-001" for etiqueta in producto_db.etiquetas for p in etiqueta.productos
    )


def test_eliminar_pedido_elimina_sus_detalles(db_session):
    # Dado un pedido con un detalle de producto
    categoria = CategoriaModel(nombre="Accesorios de Instalacion")
    producto = ProductoModel(
        sku="ACC-001",
        nombre="Roseta optica 2 puertos",
        precio=18.0,
        stock=80,
        categoria=categoria,
    )
    cliente = ClienteModel(nombre="Maria Huaman", documento="45678912")
    pedido = PedidoModel(cliente=cliente, total=36.0)
    DetallePedidoModel(
        pedido=pedido,
        producto=producto,
        cantidad=2,
        precio_unitario=18.0,
        subtotal=36.0,
    )
    db_session.add(pedido)
    db_session.commit()
    pedido_id = pedido.id

    # Cuando se elimina el pedido
    db_session.delete(pedido)
    db_session.commit()

    # Entonces sus detalles desaparecen y el producto se conserva
    cantidad_detalles = db_session.scalar(
        select(func.count(DetallePedidoModel.id)).where(DetallePedidoModel.pedido_id == pedido_id)
    )
    producto_db = db_session.scalars(
        select(ProductoModel).where(ProductoModel.sku == "ACC-001")
    ).first()
    assert cantidad_detalles == 0
    assert producto_db is not None


def test_documento_de_cliente_es_unico(db_session):
    # Dado un cliente persistido
    db_session.add(ClienteModel(nombre="Cliente Uno", documento="11112222"))
    db_session.commit()

    # Cuando se intenta guardar otro cliente con el mismo documento
    db_session.add(ClienteModel(nombre="Cliente Dos", documento="11112222"))

    # Entonces la restriccion UNIQUE impide el commit
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
