"""Fixtures compartidos por la suite de pruebas de OptiFiber."""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.infraestructura.modelos import Base


@pytest.fixture(scope="function")
def db_session():
    """Sesion limpia de SQLite en memoria para cada prueba.

    ``StaticPool`` mantiene una sola conexion para que todas las operaciones
    vean la misma base de datos en memoria durante la prueba.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _activar_claves_foraneas(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()
