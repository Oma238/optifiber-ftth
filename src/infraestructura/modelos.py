"""Modelos ORM de OptiFiber FTTH - version inicial del taller."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Clase base declarativa para todas las entidades ORM."""
