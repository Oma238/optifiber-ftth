"""Modelos ORM de OptiFiber FTTH.

Diseno del ERD (PBI-02):

* Cliente 1:N Pedido (cascada al eliminar el cliente).
* Pedido 1:N DetallePedido (cascada al eliminar el pedido).
* Categoria 1:N Producto.
* Producto N:M Etiqueta mediante la tabla de asociacion ``producto_etiqueta``.
* Producto 1:N DetallePedido.

La logica de negocio (totales, descuentos y validacion de stock) vive en
``src/dominio``. Este modulo solo describe la persistencia.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Clase base declarativa para todas las entidades ORM."""


# La tabla de asociacion debe declararse antes que las clases que la usan.
producto_etiqueta = Table(
    "producto_etiqueta",
    Base.metadata,
    Column(
        "producto_id",
        Integer,
        ForeignKey("productos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "etiqueta_id",
        Integer,
        ForeignKey("etiquetas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ClienteModel(Base):
    """Cliente persona natural o empresa que compra productos FTTH."""

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

    def __repr__(self) -> str:
        return f"ClienteModel(id={self.id!r}, documento={self.documento!r}, nombre={self.nombre!r})"


class CategoriaModel(Base):
    """Categoria comercial del catalogo (fibra, equipos, accesorios, etc.)."""

    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(200), nullable=False, default="")

    productos: Mapped[list[ProductoModel]] = relationship(back_populates="categoria")

    def __repr__(self) -> str:
        return f"CategoriaModel(id={self.id!r}, nombre={self.nombre!r})"


class EtiquetaModel(Base):
    """Etiqueta reutilizable para clasificar productos (hogar, empresa, etc.)."""

    __tablename__ = "etiquetas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    productos: Mapped[list[ProductoModel]] = relationship(
        secondary=producto_etiqueta,
        back_populates="etiquetas",
    )

    def __repr__(self) -> str:
        return f"EtiquetaModel(id={self.id!r}, nombre={self.nombre!r})"


class ProductoModel(Base):
    """Producto FTTH vendido por OptiFiber."""

    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("precio >= 0", name="ck_productos_precio_no_negativo"),
        CheckConstraint("stock >= 0", name="ck_productos_stock_no_negativo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(nullable=False, default=True)
    categoria_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categorias.id", ondelete="RESTRICT"),
        nullable=False,
    )

    categoria: Mapped[CategoriaModel] = relationship(back_populates="productos")
    etiquetas: Mapped[list[EtiquetaModel]] = relationship(
        secondary=producto_etiqueta,
        back_populates="productos",
    )
    detalles: Mapped[list[DetallePedidoModel]] = relationship(back_populates="producto")

    def __repr__(self) -> str:
        return f"ProductoModel(id={self.id!r}, sku={self.sku!r}, nombre={self.nombre!r})"


class PedidoModel(Base):
    """Pedido realizado por un cliente."""

    __tablename__ = "pedidos"
    __table_args__ = (CheckConstraint("total >= 0", name="ck_pedidos_total_no_negativo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")
    total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cliente_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clientes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    cliente: Mapped[ClienteModel] = relationship(back_populates="pedidos")
    detalles: Mapped[list[DetallePedidoModel]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
        order_by="DetallePedidoModel.id",
    )

    def __repr__(self) -> str:
        return f"PedidoModel(id={self.id!r}, estado={self.estado!r}, total={self.total!r})"


class DetallePedidoModel(Base):
    """Linea de pedido: resuelve la relacion N:M entre Pedido y Producto."""

    __tablename__ = "detalle_pedidos"
    __table_args__ = (
        UniqueConstraint("pedido_id", "producto_id", name="uq_detalle_pedido_producto"),
        CheckConstraint("cantidad > 0", name="ck_detalle_cantidad_positiva"),
        CheckConstraint("precio_unitario >= 0", name="ck_detalle_precio_no_negativo"),
        CheckConstraint("subtotal >= 0", name="ck_detalle_subtotal_no_negativo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("pedidos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    producto_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("productos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    pedido: Mapped[PedidoModel] = relationship(back_populates="detalles")
    producto: Mapped[ProductoModel] = relationship(back_populates="detalles")

    def __repr__(self) -> str:
        return (
            f"DetallePedidoModel(id={self.id!r}, producto_id={self.producto_id!r}, "
            f"cantidad={self.cantidad!r}, subtotal={self.subtotal!r})"
        )
