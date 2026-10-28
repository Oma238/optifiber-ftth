"""Interfaz de linea de comandos de OptiFiber FTTH."""

from __future__ import annotations

import argparse
import sys

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.dominio.servicios import (
    ErrorDominio,
    calcular_descuento,
    calcular_subtotal,
    calcular_total_pedido,
    validar_cantidad,
    validar_stock,
)
from src.infraestructura.db import crear_engine, crear_session_factory, inicializar_db
from src.infraestructura.modelos import PedidoModel
from src.infraestructura.repositorios import (
    CatalogoRepositorio,
    ClienteRepositorio,
    PedidoRepositorio,
)
from src.infraestructura.seed import sembrar_datos


def formato_moneda(valor: float) -> str:
    """Devuelve un monto con separador de miles y dos decimales."""
    return f"S/ {valor:,.2f}"


def truncar(texto: str, ancho: int) -> str:
    """Recorta un texto para que las tablas de consola queden alineadas."""
    return texto if len(texto) <= ancho else f"{texto[: ancho - 1]}…"


def mostrar_catalogo(session: Session) -> None:
    productos = CatalogoRepositorio(session).listar_productos()
    print("\nCATALOGO DE PRODUCTOS FTTH")
    print("-" * 118)
    print(
        f"{'SKU':<10} {'Producto':<36} {'Categoria':<26} {'Precio':>12} {'Stock':>6}  Etiquetas"
    )
    print("-" * 118)
    for producto in productos:
        etiquetas = ", ".join(etiqueta.nombre for etiqueta in producto.etiquetas)
        print(
            f"{producto.sku:<10} "
            f"{truncar(producto.nombre, 36):<36} "
            f"{truncar(producto.categoria.nombre, 26):<26} "
            f"{formato_moneda(producto.precio):>12} "
            f"{producto.stock:>6}  "
            f"{etiquetas}"
        )
    print("-" * 118)
    print(f"Total de productos activos: {len(productos)}")


def listar_clientes(session: Session) -> None:
    clientes = ClienteRepositorio(session).listar()
    print("\nCLIENTES REGISTRADOS")
    print("-" * 92)
    print(f"{'ID':>4}  {'Documento':<12} {'Cliente':<30} {'Telefono':<12} {'Pedidos':>7}")
    print("-" * 92)
    for cliente in clientes:
        print(
            f"{cliente.id:>4}  {cliente.documento:<12} "
            f"{truncar(cliente.nombre, 30):<30} "
            f"{cliente.telefono:<12} {len(cliente.pedidos):>7}"
        )
    print("-" * 92)
    print(f"Total de clientes: {len(clientes)}")


def registrar_cliente(session: Session) -> None:
    print("\nNUEVO CLIENTE")
    nombre = input("Nombre completo o razon social: ").strip()
    documento = input("DNI (8 digitos) o RUC (11 digitos): ").strip()
    telefono = input("Telefono: ").strip()
    email = input("Correo electronico: ").strip()
    direccion = input("Direccion: ").strip()

    cliente = ClienteRepositorio(session).crear(
        nombre=nombre,
        documento=documento,
        telefono=telefono,
        email=email,
        direccion=direccion,
    )
    print(f"\n[OK] Cliente registrado: {cliente.nombre} (documento {cliente.documento}).")


def _leer_cantidad(producto_stock: int) -> int:
    texto = input(f"Cantidad (stock disponible {producto_stock}): ").strip()
    try:
        cantidad = int(texto)
    except ValueError as exc:
        raise ErrorDominio("La cantidad debe ser un numero entero.") from exc
    return validar_cantidad(cantidad)


def registrar_pedido(session: Session) -> None:
    cliente_repo = ClienteRepositorio(session)
    catalogo = CatalogoRepositorio(session)
    pedido_repo = PedidoRepositorio(session)

    print("\nNUEVO PEDIDO")
    documento = input("Documento del cliente: ").strip()
    cliente = cliente_repo.buscar_por_documento(documento)
    if cliente is None:
        print(f"[ERROR] No existe un cliente con el documento {documento}.")
        return

    print(f"Cliente: {cliente.nombre}")
    mostrar_catalogo(session)

    items: dict[str, int] = {}
    while True:
        sku = input("\nSKU del producto (Enter para terminar): ").strip().upper()
        if not sku:
            break

        producto = catalogo.buscar_por_sku(sku)
        if producto is None:
            print(f"[ERROR] No existe el producto {sku}.")
            continue

        try:
            cantidad = _leer_cantidad(producto.stock)
            validar_stock(items.get(sku, 0) + cantidad, producto.stock)
        except ErrorDominio as exc:
            print(f"[ERROR] {exc}")
            continue

        items[sku] = items.get(sku, 0) + cantidad
        print(f"  Agregado: {producto.nombre} x {cantidad}")

    if not items:
        print("[AVISO] No se agregaron productos. Pedido cancelado.")
        return

    lineas: list[tuple[int, float]] = []
    print("\nRESUMEN DEL PEDIDO")
    print("-" * 74)
    for sku, cantidad in items.items():
        producto = catalogo.buscar_por_sku(sku)
        if producto is None:  # pragma: no cover - defensa ante cambios concurrentes
            raise ErrorDominio(f"El producto {sku} dejo de existir.")
        subtotal = calcular_subtotal(cantidad, producto.precio)
        lineas.append((cantidad, producto.precio))
        print(f"  {producto.nombre:<40} x{cantidad:>3}  {formato_moneda(subtotal):>12}")

    total_sin_descuento = sum(calcular_subtotal(c, p) for c, p in lineas)
    descuento = calcular_descuento(total_sin_descuento)
    total = calcular_total_pedido(lineas)
    print("-" * 74)
    if descuento:
        print(f"  Subtotal: {formato_moneda(total_sin_descuento)}")
        print(f"  Descuento por volumen (5%): -{formato_moneda(descuento)}")
    print(f"  TOTAL A PAGAR: {formato_moneda(total)}")

    confirmar = input("\n¿Confirmar pedido? (S/N): ").strip().lower()
    if confirmar not in {"s", "si", "sí"}:
        print("[AVISO] Pedido cancelado. No se modifico el stock.")
        return

    pedido = pedido_repo.crear_pedido(documento, list(items.items()))
    print(f"\n[OK] Pedido #{pedido.id} registrado por {formato_moneda(pedido.total)}.")
    mostrar_pedido(session, pedido)


def mostrar_pedido(session: Session, pedido: PedidoModel) -> None:
    pedido_db = PedidoRepositorio(session).obtener(pedido.id) or pedido
    print("-" * 82)
    print(
        f"Pedido #{pedido_db.id} | {pedido_db.fecha} | {pedido_db.estado} | "
        f"{pedido_db.cliente.nombre} ({pedido_db.cliente.documento})"
    )
    for detalle in pedido_db.detalles:
        print(
            f"  - {detalle.producto.nombre:<40} x{detalle.cantidad:>3} "
            f"{formato_moneda(detalle.precio_unitario):>11} = "
            f"{formato_moneda(detalle.subtotal):>12}"
        )
    print(f"  TOTAL: {formato_moneda(pedido_db.total)}")
    print("-" * 82)


def listar_pedidos(session: Session) -> None:
    pedidos = PedidoRepositorio(session).listar()
    print("\nHISTORIAL DE PEDIDOS")
    if not pedidos:
        print("Aun no hay pedidos registrados.")
        return

    for pedido in pedidos:
        mostrar_pedido(session, pedido)


def mostrar_reporte(session: Session) -> None:
    pedido_repo = PedidoRepositorio(session)
    catalogo = CatalogoRepositorio(session)

    print("\nREPORTE DE VENTAS")
    print("-" * 62)
    resumen = pedido_repo.resumen_ventas()
    if not resumen:
        print("Sin pedidos registrados.")
    else:
        print(f"{'Estado':<14} {'Pedidos':>10} {'Monto':>16}")
        for estado, datos in resumen.items():
            print(f"{estado:<14} {int(datos['cantidad']):>10} {formato_moneda(datos['total']):>16}")

    print("\nPRODUCTOS MAS VENDIDOS")
    print("-" * 78)
    top = pedido_repo.productos_mas_vendidos()
    if not top:
        print("Sin ventas registradas.")
    else:
        print(f"{'SKU':<10} {'Producto':<38} {'Unidades':>9} {'Ingresos':>14}")
        for fila in top:
            print(
                f"{fila['sku']:<10} {truncar(str(fila['nombre']), 38):<38} "
                f"{fila['unidades']:>9} {formato_moneda(float(fila['ingresos'])):>14}"
            )

    print("\nALERTA DE STOCK BAJO (<= 5 unidades)")
    print("-" * 62)
    stock_bajo = catalogo.stock_bajo(limite=5)
    if not stock_bajo:
        print("Todos los productos tienen stock suficiente.")
    else:
        for producto in stock_bajo:
            print(f"  {producto.sku:<10} {producto.nombre:<40} stock: {producto.stock}")


def eliminar_cliente(session: Session) -> None:
    cliente_repo = ClienteRepositorio(session)
    documento = input("\nDocumento del cliente a eliminar: ").strip()
    cliente = cliente_repo.buscar_por_documento(documento)
    if cliente is None:
        print(f"[ERROR] No existe un cliente con el documento {documento}.")
        return

    print(
        f"\n[AVISO] Se eliminara a {cliente.nombre} y sus {len(cliente.pedidos)} pedido(s). "
        "La operacion aplica cascada en la base de datos."
    )
    confirmar = input("Escriba SI para confirmar: ").strip().upper()
    if confirmar != "SI":
        print("[AVISO] Operacion cancelada.")
        return

    cliente_repo.eliminar(cliente.id)
    print(f"[OK] Cliente {cliente.nombre} eliminado junto con sus pedidos.")


def ejecutar_demo(session: Session) -> None:
    """Recorre el flujo principal sin pedir datos por teclado."""
    cliente_repo = ClienteRepositorio(session)
    pedido_repo = PedidoRepositorio(session)

    print("\n" + "=" * 78)
    print(" DEMO FUNCIONAL OPTIFIBER - PERSISTENCIA ORM SQLALCHEMY")
    print("=" * 78)

    mostrar_catalogo(session)
    listar_clientes(session)

    pedidos = pedido_repo.listar()
    if not pedidos:
        pedido = pedido_repo.crear_pedido(
            "20512345678",
            [("FIB-002", 2), ("RED-001", 1), ("ACC-002", 4)],
        )
        print("\nPedido corporativo de demostracion creado con descuento por volumen.")
        mostrar_pedido(session, pedido)
    else:
        print("\nPedido existente en la base de datos:")
        mostrar_pedido(session, pedidos[0])

    # Evidencia de eliminacion en cascada: cliente temporal -> pedido -> detalle.
    temporal = cliente_repo.buscar_por_documento("99999999")
    if temporal is None:
        temporal = cliente_repo.crear(
            "Cliente Temporal Demo",
            "99999999",
            telefono="900000000",
            email="demo@optifiber.local",
            direccion="Sede temporal",
        )
        pedido_repo.crear_pedido("99999999", [("ACC-001", 1)])

    pedido_temporal_id = temporal.pedidos[0].id if temporal.pedidos else None
    cliente_repo.eliminar(temporal.id)
    pedido_eliminado = (
        pedido_repo.obtener(pedido_temporal_id) is None if pedido_temporal_id else True
    )
    print(
        "\n[CASCADA] Cliente temporal eliminado; pedido dependiente eliminado: "
        f"{'SI' if pedido_eliminado else 'NO'}."
    )

    print("\n[OK] Demo finalizada. La persistencia, las relaciones y la cascada funcionan.")
    print("=" * 78)


def mostrar_menu() -> None:
    print("\n" + "=" * 58)
    print(" OPTIFIBER - GESTION DE PRODUCTOS FTTH")
    print("=" * 58)
    print(" 1. Ver catalogo de productos")
    print(" 2. Registrar cliente")
    print(" 3. Listar clientes")
    print(" 4. Registrar pedido")
    print(" 5. Listar pedidos")
    print(" 6. Reporte de ventas y stock bajo")
    print(" 7. Eliminar cliente (demostrar cascada)")
    print(" 0. Salir")
    print("=" * 58)


def menu_interactivo(session: Session) -> None:
    acciones = {
        "1": mostrar_catalogo,
        "2": registrar_cliente,
        "3": listar_clientes,
        "4": registrar_pedido,
        "5": listar_pedidos,
        "6": mostrar_reporte,
        "7": eliminar_cliente,
    }

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "0":
            print("\nGracias por usar OptiFiber. Hasta pronto.")
            return
        accion = acciones.get(opcion)
        if accion is None:
            print("[ERROR] Opcion no valida. Intente nuevamente.")
            continue
        try:
            accion(session)
        except ErrorDominio as exc:
            session.rollback()
            print(f"[ERROR] {exc}")
        except SQLAlchemyError as exc:
            session.rollback()
            print(f"[ERROR] No se pudo completar la operacion: {exc}")


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):  # pragma: no cover - depende de la consola
        pass

    parser = argparse.ArgumentParser(description="Gestion de productos FTTH de OptiFiber.")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Ejecuta un flujo de demostracion sin interaccion (usa SQLite en memoria).",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="URL SQLAlchemy de la base de datos. Por defecto: data/optifiber.db",
    )
    args = parser.parse_args(argv)

    url = "sqlite:///:memory:" if args.demo and args.db is None else args.db
    engine = crear_engine(url)
    inicializar_db(engine)
    session_factory = crear_session_factory(engine)

    with session_factory() as session:
        sembrar_datos(session)
        if args.demo:
            ejecutar_demo(session)
        else:
            try:
                menu_interactivo(session)
            except (KeyboardInterrupt, EOFError):
                print("\n\nSesion finalizada.")
    engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
