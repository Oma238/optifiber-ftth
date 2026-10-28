"""Configuracion de la conexion SQLAlchemy y creacion del esquema."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from src.infraestructura.modelos import Base

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_DB_PREDETERMINADA = RAIZ_PROYECTO / "data" / "optifiber.db"
URL_DB_PREDETERMINADA = f"sqlite:///{RUTA_DB_PREDETERMINADA.as_posix()}"


def crear_engine(url: str | None = None) -> Engine:
    """Crea un engine SQLAlchemy y activa las claves foraneas en SQLite."""
    url = url or URL_DB_PREDETERMINADA
    url_obj = make_url(url)

    if url_obj.drivername.startswith("sqlite") and url_obj.database not in {None, ":memory:"}:
        Path(url_obj.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(url, future=True)

    if url_obj.drivername.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _activar_claves_foraneas(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def crear_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Fabrica sesiones que no expiran los objetos al hacer commit."""
    return sessionmaker(bind=engine, expire_on_commit=False)


def inicializar_db(engine: Engine) -> None:
    """Crea todas las tablas declaradas en los modelos ORM."""
    Base.metadata.create_all(bind=engine)
