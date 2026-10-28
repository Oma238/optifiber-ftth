"""Pruebas de persistencia ORM del PBI-02: ciclo 1."""

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
