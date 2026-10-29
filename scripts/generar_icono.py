"""Genera el icono de la aplicacion OptiFiber (assets/optifiber.ico)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "assets" / "optifiber.ico"

FONDO = "#0B1118"
ACENTO = "#2DD4BF"
TEXTO = "#F4F7FB"
TENUE = "#7D8B9D"


def construir() -> Image.Image:
    """Dibuja un icono minimalista: marco redondeado y anillo de fibra."""
    escala = 4
    lado = 256 * escala
    imagen = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(imagen)

    margen = 14 * escala
    radio = 52 * escala
    dibujo.rounded_rectangle(
        (margen, margen, lado - margen, lado - margen),
        radius=radio,
        fill=FONDO,
        outline=ACENTO,
        width=7 * escala,
    )

    centro = lado // 2
    desplazamiento = 8 * escala
    grosor = 16 * escala
    caja_exterior = (
        centro - 58 * escala,
        centro - 66 * escala + desplazamiento,
        centro + 58 * escala,
        centro + 50 * escala + desplazamiento,
    )
    dibujo.ellipse(caja_exterior, outline=ACENTO, width=grosor)

    linea_y = centro + 74 * escala
    dibujo.line(
        (
            centro - 44 * escala,
            linea_y,
            centro + 44 * escala,
            linea_y,
        ),
        fill=TENUE,
        width=4 * escala,
    )
    for x in (centro - 44 * escala, centro + 44 * escala):
        dibujo.ellipse(
            (x - 6 * escala, linea_y - 6 * escala, x + 6 * escala, linea_y + 6 * escala),
            fill=ACENTO,
        )

    dibujo.ellipse(
        (
            centro - 9 * escala,
            centro - 9 * escala + desplazamiento,
            centro + 9 * escala,
            centro + 9 * escala + desplazamiento,
        ),
        fill=TEXTO,
    )

    return imagen.resize((256, 256), Image.Resampling.LANCZOS)


def main() -> None:
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    icono = construir()
    icono.save(
        DESTINO,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    icono.save(DESTINO.with_suffix(".png"), format="PNG")
    print(f"Icono generado en {DESTINO}")


if __name__ == "__main__":
    main()
