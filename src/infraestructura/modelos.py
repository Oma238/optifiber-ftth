"""Modelos ORM de OptiFiber FTTH - ciclo 2: cascada Cliente-Pedido."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Clase base declarativa para todas las entidades ORM."""


class ClienteModel(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    documento: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    direccion: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    pedidos: Mapped[list[PedidoModel]] = relationship(
        back_populates="cliente",
        cascade="all, delete-orphan",
        order_by="PedidoModel.id",
    )


class PedidoModel(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")
    total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cliente_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clientes.id"),
        nullable=False,
        index=True,
    )

    cliente: Mapped[ClienteModel] = relationship(back_populates="pedidos")
