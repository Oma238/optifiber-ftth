"""Repositorios de OptiFiber: traducen operaciones de negocio a SQLAlchemy."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from src.dominio.servicios import (
    ErrorDominio,
    calcular_subtotal,
    calcular_total_pedido,
    validar_cantidad,
    validar_documento,
    validar_stock,
)
from src.infraestructura.modelos import (
    CategoriaModel,
    ClienteModel,
    DetallePedidoModel,
    EtiquetaModel,
    PedidoModel,
    ProductoModel,
)

ESTADOS_PEDIDO = {"PENDIENTE", "PAGADO", "ENVIADO", "CANCELADO"}


class ClienteRepositorio:
    """Operaciones de persistencia para clientes."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def listar(self) -> list[ClienteModel]:
        stmt = (
            select(ClienteModel)
            .options(selectinload(ClienteModel.pedidos))
            .order_by(ClienteModel.nombre)
        )
        return list(self.session.scalars(stmt))

    def buscar_por_documento(self, documento: str) -> ClienteModel | None:
        stmt = select(ClienteModel).where(ClienteModel.documento == documento.strip())
        return self.session.scalars(stmt).first()

    def crear(
        self,
        nombre: str,
        documento: str,
        telefono: str = "",
        email: str = "",
        direccion: str = "",
    ) -> ClienteModel:
        nombre = nombre.strip()
        if not nombre:
            raise ErrorDominio("El nombre del cliente es obligatorio.")
        documento = validar_documento(documento)

        if self.buscar_por_documento(documento) is not None:
            raise ErrorDominio(f"Ya existe un cliente con el documento {documento}.")

        cliente = ClienteModel(
            nombre=nombre,
            documento=documento,
            telefono=telefono.strip(),
            email=email.strip(),
            direccion=direccion.strip(),
        )
        self.session.add(cliente)
        self.session.commit()
        self.session.refresh(cliente)
        return cliente

    def eliminar(self, cliente_id: int) -> bool:
        cliente = self.session.get(ClienteModel, cliente_id)
        if cliente is None:
            return False
        self.session.delete(cliente)
        self.session.commit()
        return True


class CatalogoRepositorio:
    """Operaciones de persistencia para categorias, productos y etiquetas."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def listar_categorias(self) -> list[CategoriaModel]:
        return list(self.session.scalars(select(CategoriaModel).order_by(CategoriaModel.nombre)))

    def listar_productos(self, solo_activos: bool = True) -> list[ProductoModel]:
        stmt = select(ProductoModel).options(
            selectinload(ProductoModel.categoria),
            selectinload(ProductoModel.etiquetas),
        )
        if solo_activos:
            stmt = stmt.where(ProductoModel.activo.is_(True))
        stmt = stmt.order_by(ProductoModel.nombre)
        return list(self.session.scalars(stmt))

    def buscar_por_sku(self, sku: str) -> ProductoModel | None:
        stmt = (
            select(ProductoModel)
            .options(
                selectinload(ProductoModel.categoria),
                selectinload(ProductoModel.etiquetas),
            )
            .where(ProductoModel.sku == sku.strip().upper())
        )
        return self.session.scalars(stmt).first()

    def crear_categoria(self, nombre: str, descripcion: str = "") -> CategoriaModel:
        nombre = nombre.strip()
        if not nombre:
            raise ErrorDominio("El nombre de la categoria es obligatorio.")
        existente = self.session.scalars(
            select(CategoriaModel).where(CategoriaModel.nombre == nombre)
        ).first()
        if existente is not None:
            raise ErrorDominio(f"La categoria {nombre} ya existe.")

        categoria = CategoriaModel(nombre=nombre, descripcion=descripcion.strip())
        self.session.add(categoria)
        self.session.commit()
        self.session.refresh(categoria)
        return categoria

    def crear_producto(
        self,
        sku: str,
        nombre: str,
        precio: float,
        stock: int,
        categoria_id: int,
        descripcion: str = "",
        etiquetas: Sequence[str] = (),
    ) -> ProductoModel:
        sku = sku.strip().upper()
        nombre = nombre.strip()
        if not sku or not nombre:
            raise ErrorDominio("El SKU y el nombre del producto son obligatorios.")
        if precio < 0:
            raise ErrorDominio("El precio no puede ser negativo.")
        if stock < 0:
            raise ErrorDominio("El stock no puede ser negativo.")
        if self.buscar_por_sku(sku) is not None:
            raise ErrorDominio(f"Ya existe un producto con el SKU {sku}.")

        categoria = self.session.get(CategoriaModel, categoria_id)
        if categoria is None:
            raise ErrorDominio("La categoria indicada no existe.")

        producto = ProductoModel(
            sku=sku,
            nombre=nombre,
            descripcion=descripcion.strip(),
            precio=precio,
            stock=stock,
            categoria=categoria,
        )
        self.session.add(producto)

        for nombre_etiqueta in etiquetas:
            etiqueta = self.session.scalars(
                select(EtiquetaModel).where(EtiquetaModel.nombre == nombre_etiqueta.strip())
            ).first()
            if etiqueta is None:
                etiqueta = EtiquetaModel(nombre=nombre_etiqueta.strip())
            producto.etiquetas.append(etiqueta)

        self.session.commit()
        self.session.refresh(producto)
        return producto

    def stock_bajo(self, limite: int = 5) -> list[ProductoModel]:
        stmt = (
            select(ProductoModel)
            .where(ProductoModel.activo.is_(True), ProductoModel.stock <= limite)
            .order_by(ProductoModel.stock, ProductoModel.nombre)
        )
        return list(self.session.scalars(stmt))

    def productos_por_categoria(self, categoria_id: int) -> list[ProductoModel]:
        stmt = (
            select(ProductoModel)
            .where(ProductoModel.categoria_id == categoria_id)
            .order_by(ProductoModel.nombre)
        )
        return list(self.session.scalars(stmt))


class PedidoRepositorio:
    """Operaciones de persistencia para pedidos y sus detalles."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _consulta_base(self):
        return select(PedidoModel).options(
            selectinload(PedidoModel.cliente),
            selectinload(PedidoModel.detalles).selectinload(DetallePedidoModel.producto),
        )

    def listar(self) -> list[PedidoModel]:
        stmt = self._consulta_base().order_by(PedidoModel.fecha.desc(), PedidoModel.id.desc())
        return list(self.session.scalars(stmt))

    def obtener(self, pedido_id: int) -> PedidoModel | None:
        stmt = self._consulta_base().where(PedidoModel.id == pedido_id)
        return self.session.scalars(stmt).first()

    def crear_pedido(
        self,
        documento_cliente: str,
        items: Sequence[tuple[str, int]],
        estado: str = "PENDIENTE",
    ) -> PedidoModel:
        """Crea un pedido, valida stock, descuenta inventario y calcula totales."""
        if not items:
            raise ErrorDominio("El pedido debe tener al menos un producto.")
        if estado not in ESTADOS_PEDIDO:
            raise ErrorDominio(f"Estado de pedido no valido: {estado}.")

        documento = documento_cliente.strip()
        cliente = self.session.scalars(
            select(ClienteModel).where(ClienteModel.documento == documento)
        ).first()
        if cliente is None:
            raise ErrorDominio(f"No existe un cliente con el documento {documento}.")

        pedido = PedidoModel(cliente=cliente, estado=estado)
        lineas: list[tuple[int, float]] = []
        skus_vistos: set[str] = set()

        try:
            with self.session.no_autoflush:
                for sku, cantidad in items:
                    sku_normalizado = sku.strip().upper()
                    if sku_normalizado in skus_vistos:
                        raise ErrorDominio(
                            f"El producto {sku_normalizado} esta repetido en el pedido."
                        )
                    skus_vistos.add(sku_normalizado)

                    producto = self.session.scalars(
                        select(ProductoModel).where(ProductoModel.sku == sku_normalizado)
                    ).first()
                    if producto is None:
                        raise ErrorDominio(f"No existe un producto con el SKU {sku_normalizado}.")

                    validar_cantidad(cantidad)
                    validar_stock(cantidad, producto.stock)

                    subtotal = calcular_subtotal(cantidad, producto.precio)
                    detalle = DetallePedidoModel(
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio,
                        subtotal=subtotal,
                    )
                    pedido.detalles.append(detalle)
                    lineas.append((cantidad, producto.precio))
                    producto.stock -= cantidad

            pedido.total = calcular_total_pedido(lineas)
            self.session.add(pedido)
            self.session.commit()
            self.session.refresh(pedido)
            return pedido
        except Exception:
            self.session.rollback()
            raise

    def cambiar_estado(self, pedido_id: int, estado: str) -> PedidoModel:
        if estado not in ESTADOS_PEDIDO:
            raise ErrorDominio(f"Estado de pedido no valido: {estado}.")
        pedido = self.session.get(PedidoModel, pedido_id)
        if pedido is None:
            raise ErrorDominio(f"No existe el pedido {pedido_id}.")
        pedido.estado = estado
        self.session.commit()
        self.session.refresh(pedido)
        return pedido

    def eliminar(self, pedido_id: int) -> bool:
        pedido = self.session.get(PedidoModel, pedido_id)
        if pedido is None:
            return False
        self.session.delete(pedido)
        self.session.commit()
        return True

    def resumen_ventas(self) -> dict[str, dict[str, float]]:
        stmt = (
            select(
                PedidoModel.estado,
                func.count(PedidoModel.id),
                func.coalesce(func.sum(PedidoModel.total), 0.0),
            )
            .group_by(PedidoModel.estado)
            .order_by(PedidoModel.estado)
        )
        return {
            estado: {"cantidad": float(cantidad), "total": float(total)}
            for estado, cantidad, total in self.session.execute(stmt).all()
        }

    def productos_mas_vendidos(self, limite: int = 5) -> list[dict[str, object]]:
        stmt = (
            select(
                ProductoModel.sku,
                ProductoModel.nombre,
                func.sum(DetallePedidoModel.cantidad).label("unidades"),
                func.sum(DetallePedidoModel.subtotal).label("ingresos"),
            )
            .join(DetallePedidoModel, DetallePedidoModel.producto_id == ProductoModel.id)
            .group_by(ProductoModel.id, ProductoModel.sku, ProductoModel.nombre)
            .order_by(func.sum(DetallePedidoModel.cantidad).desc())
            .limit(limite)
        )
        return [
            {
                "sku": sku,
                "nombre": nombre,
                "unidades": int(unidades or 0),
                "ingresos": float(ingresos or 0.0),
            }
            for sku, nombre, unidades, ingresos in self.session.execute(stmt).all()
        ]
