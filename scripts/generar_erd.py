"""Genera el diagrama ERD de OptiFiber en PNG para el informe y el README."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "docs" / "erd_optifiber.png"

ANCHO, ALTO = 1900, 1150
FONDO = "#f8fafc"
TEXTO = "#0f172a"
TEXTO_SUAVE = "#475569"
BORDE = "#cbd5e1"
BLANCO = "#ffffff"


def fuente(nombre: str, tamano: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    rutas = [
        Path("C:/Windows/Fonts") / nombre,
        Path("/usr/share/fonts/truetype/dejavu") / nombre,
    ]
    for ruta in rutas:
        if ruta.exists():
            return ImageFont.truetype(str(ruta), tamano)
    return ImageFont.load_default(size=tamano)


FUENTE_TITULO = fuente("segoeuib.ttf", 34)
FUENTE_SUBTITULO = fuente("segoeui.ttf", 19)
FUENTE_ENTIDAD = fuente("segoeuib.ttf", 20)
FUENTE_CAMPO = fuente("consola.ttf", 17)
FUENTE_CAMPO_BOLD = fuente("consolab.ttf", 17)
FUENTE_ETIQUETA = fuente("segoeuib.ttf", 16)
FUENTE_PEQUENA = fuente("segoeui.ttf", 15)


def caja_entidad(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    ancho: float,
    titulo: str,
    color: str,
    campos: list[tuple[str, str, str]],
) -> tuple[int, int, int, int]:
    alto = 42 + len(campos) * 27 + 16
    # Sombra
    draw.rounded_rectangle(
        [x + 5, y + 6, x + ancho + 5, y + alto + 6],
        radius=14,
        fill="#e2e8f0",
    )
    # Cuerpo
    draw.rounded_rectangle(
        [x, y, x + ancho, y + alto],
        radius=14,
        fill=BLANCO,
        outline=BORDE,
        width=2,
    )
    # Encabezado
    draw.rounded_rectangle([x, y, x + ancho, y + 42], radius=14, fill=color)
    draw.rectangle([x, y + 30, x + ancho, y + 42], fill=color)
    draw.text((x + 16, y + 10), titulo, font=FUENTE_ENTIDAD, fill=BLANCO)

    for indice, (tipo, nombre, detalle) in enumerate(campos):
        fila_y = y + 50 + indice * 27
        color_tipo = {"PK": "#b45309", "FK": "#1d4ed8", "UQ": "#6d28d9"}.get(tipo, TEXTO_SUAVE)
        if tipo:
            draw.text((x + 14, fila_y), tipo, font=FUENTE_CAMPO_BOLD, fill=color_tipo)
        draw.text((x + 54, fila_y), nombre, font=FUENTE_CAMPO, fill=TEXTO)
        if detalle:
            ancho_detalle = draw.textlength(detalle, font=FUENTE_CAMPO)
            draw.text(
                (x + ancho - ancho_detalle - 14, fila_y),
                detalle,
                font=FUENTE_CAMPO,
                fill=TEXTO_SUAVE,
            )
    return (x, y, int(x + ancho), y + alto)


def etiqueta_linea(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    texto: str,
    color: str = "#334155",
) -> None:
    bbox = draw.textbbox((x, y), texto, font=FUENTE_PEQUENA)
    draw.rounded_rectangle(
        [bbox[0] - 7, bbox[1] - 3, bbox[2] + 7, bbox[3] + 3],
        radius=5,
        fill=FONDO,
        outline="#e2e8f0",
    )
    draw.text((x, y), texto, font=FUENTE_PEQUENA, fill=color)


def pie_de_cuervo(draw: ImageDraw.ImageDraw, x: int, y: int, direccion: str, color: str) -> None:
    if direccion in {"izquierda", "derecha"}:
        signo = -1 if direccion == "izquierda" else 1
        for delta in (-10, 0, 10):
            draw.line([(x, y), (x + signo * 13, y + delta)], fill=color, width=2)
    else:
        signo = -1 if direccion == "arriba" else 1
        for delta in (-10, 0, 10):
            draw.line([(x, y), (x + delta, y + signo * 13)], fill=color, width=2)


def linea_uno(draw: ImageDraw.ImageDraw, x: int, y: int, orientacion: str, color: str) -> None:
    if orientacion == "vertical":
        draw.line([(x - 7, y), (x + 7, y)], fill=color, width=3)
    else:
        draw.line([(x, y - 7), (x, y + 7)], fill=color, width=3)


def main() -> None:
    imagen = Image.new("RGB", (ANCHO, ALTO), FONDO)
    draw = ImageDraw.Draw(imagen)

    draw.text((60, 32), "OPTIFIBER · MODELO ENTIDAD-RELACIÓN", font=FUENTE_TITULO, fill=TEXTO)
    draw.text(
        (62, 78),
        "PBI-02 · Persistencia de datos, mapeo ORM y pruebas con fixtures · "
        "SQLAlchemy 2.x + SQLite",
        font=FUENTE_SUBTITULO,
        fill=TEXTO_SUAVE,
    )

    azul = "#1d4ed8"
    verde = "#047857"
    teal = "#0f766e"
    naranja = "#b45309"
    morado = "#6d28d9"
    gris = "#475569"

    # Lineas de relación (se dibujan antes que las cajas)
    draw.line([(420, 260), (450, 260), (450, 247), (480, 247)], fill=gris, width=2)
    pie_de_cuervo(draw, 480, 247, "izquierda", gris)
    linea_uno(draw, 420, 260, "vertical", gris)

    draw.line([(840, 247), (870, 247), (870, 274), (900, 274)], fill=gris, width=2)
    pie_de_cuervo(draw, 900, 274, "izquierda", gris)
    linea_uno(draw, 840, 247, "vertical", gris)

    draw.line([(1290, 274), (1360, 274)], fill=gris, width=2)
    pie_de_cuervo(draw, 1290, 274, "derecha", gris)
    linea_uno(draw, 1360, 274, "vertical", gris)

    draw.line([(1080, 650), (1080, 560), (1545, 560), (1545, 397)], fill=gris, width=2)
    pie_de_cuervo(draw, 1545, 397, "arriba", gris)
    linea_uno(draw, 1080, 650, "vertical", gris)

    draw.line([(1545, 650), (1545, 600), (1650, 600), (1650, 397)], fill=gris, width=2)
    pie_de_cuervo(draw, 1650, 397, "arriba", gris)
    pie_de_cuervo(draw, 1545, 650, "arriba", gris)

    # Entidades
    caja_entidad(
        draw,
        60,
        150,
        360,
        "CLIENTE",
        azul,
        [
            ("PK", "id", "Integer"),
            ("", "nombre", "String(120)"),
            ("UQ", "documento", "String(20)"),
            ("", "telefono", "String(20)"),
            ("", "email", "String(120)"),
            ("", "creado_en", "DateTime"),
        ],
    )
    caja_entidad(
        draw,
        480,
        150,
        360,
        "PEDIDO",
        verde,
        [
            ("PK", "id", "Integer"),
            ("", "fecha", "Date"),
            ("", "estado", "String(20)"),
            ("", "total", "Float"),
            ("FK", "cliente_id", "→ clientes.id"),
        ],
    )
    caja_entidad(
        draw,
        900,
        150,
        390,
        "DETALLE_PEDIDO",
        teal,
        [
            ("PK", "id", "Integer"),
            ("FK", "pedido_id", "→ pedidos.id"),
            ("FK", "producto_id", "→ productos.id"),
            ("", "cantidad", "Integer"),
            ("", "precio_unitario", "Float"),
            ("", "subtotal", "Float"),
            ("UQ", "pedido_id + producto_id", ""),
        ],
    )
    caja_entidad(
        draw,
        1360,
        150,
        370,
        "PRODUCTO",
        naranja,
        [
            ("PK", "id", "Integer"),
            ("UQ", "sku", "String(20)"),
            ("", "nombre", "String(120)"),
            ("", "precio", "Float"),
            ("", "stock", "Integer"),
            ("", "activo", "Boolean"),
            ("FK", "categoria_id", "→ categorias.id"),
        ],
    )
    caja_entidad(
        draw,
        900,
        650,
        360,
        "CATEGORIA",
        morado,
        [
            ("PK", "id", "Integer"),
            ("UQ", "nombre", "String(80)"),
            ("", "descripcion", "String(200)"),
        ],
    )
    caja_entidad(
        draw,
        1360,
        650,
        370,
        "ETIQUETA",
        gris,
        [
            ("PK", "id", "Integer"),
            ("UQ", "nombre", "String(50)"),
        ],
    )

    # Etiquetas de cardinalidad
    etiqueta_linea(draw, 430, 230, "1:N")
    etiqueta_linea(draw, 850, 230, "1:N")
    etiqueta_linea(draw, 1300, 252, "N:1")
    etiqueta_linea(draw, 1100, 538, "1:N")
    etiqueta_linea(draw, 1665, 570, "N:M")

    # Diamante de la tabla de asociación N:M
    draw.polygon([(1650, 488), (1670, 508), (1650, 528), (1630, 508)], fill="#e2e8f0", outline=gris)
    draw.text((1390, 496), "tabla asociación", font=FUENTE_PEQUENA, fill=TEXTO_SUAVE)

    # Leyenda
    draw.rounded_rectangle([60, 830, 1240, 1045], radius=14, fill=BLANCO, outline=BORDE, width=2)
    draw.text((82, 850), "LEYENDA Y REGLAS DE PERSISTENCIA", font=FUENTE_ETIQUETA, fill=TEXTO)
    draw.text(
        (82, 878),
        "PK = clave primaria · FK = clave foránea · UQ = restricción única · "
        "1:N / N:M = cardinalidad.",
        font=FUENTE_PEQUENA,
        fill=TEXTO_SUAVE,
    )
    draw.text(
        (82, 905),
        "Relaciones: Cliente 1:N Pedido · Pedido 1:N DetallePedido · Categoría 1:N Producto.",
        font=FUENTE_PEQUENA,
        fill=TEXTO_SUAVE,
    )
    draw.text(
        (82, 932),
        "Producto N:M Etiqueta mediante la tabla producto_etiqueta · DetallePedido N:1 Producto.",
        font=FUENTE_PEQUENA,
        fill=TEXTO_SUAVE,
    )
    draw.text(
        (82, 959),
        "Cascada ORM: Cliente → Pedido → DetallePedido con cascade=\"all, delete-orphan\".",
        font=FUENTE_PEQUENA,
        fill=TEXTO_SUAVE,
    )
    draw.text(
        (82, 986),
        "La tabla producto_etiqueta se declara con Table(...) y se enlaza con "
        "relationship(secondary=...).",
        font=FUENTE_PEQUENA,
        fill=TEXTO_SUAVE,
    )
    draw.text(
        (82, 1013),
        "Base de datos: SQLite · ORM: SQLAlchemy 2.x · Pruebas: pytest con sqlite:///:memory:.",
        font=FUENTE_PEQUENA,
        fill=TEXTO_SUAVE,
    )
    draw.text(
        (60, 1090),
        "OPTIFIBER · Venta de productos FTTH · Construcción de Software · 2026",
        font=FUENTE_PEQUENA,
        fill="#64748b",
    )

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    imagen.save(SALIDA, format="PNG", optimize=True)
    print(f"ERD generado: {SALIDA}")


if __name__ == "__main__":
    main()
