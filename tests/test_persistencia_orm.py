"""Pruebas de persistencia ORM del PBI-02: ciclos 1 y 2."""

from sqlalchemy import select

from src.infraestructura.modelos import ClienteModel, PedidoModel


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
