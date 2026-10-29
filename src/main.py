"""Punto de entrada de OptiFiber FTTH.

Uso:
    python -m src.main              # aplicacion de escritorio (interfaz grafica)
    python -m src.main --cli        # menu interactivo en la terminal
    python -m src.main --demo       # demostracion automatica en memoria
    python -m src.main --db URL     # base de datos SQLAlchemy alternativa
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gestion de productos FTTH de OptiFiber.")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Abre el menu interactivo de la terminal en lugar de la interfaz grafica.",
    )
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

    if args.cli or args.demo:
        from src.presentacion.cli import main as main_cli

        base = argv if argv is not None else sys.argv[1:]
        argumentos = [argumento for argumento in base if argumento != "--cli"]
        return main_cli(argumentos)

    try:
        from src.presentacion.gui.app import ejecutar_gui
    except ImportError as exc:  # pragma: no cover - depende del entorno grafico
        print(
            "No se pudo iniciar la interfaz grafica "
            f"({exc}). Instala las dependencias con: pip install -r requirements.txt"
        )
        print("Puedes usar la terminal con: python -m src.main --cli")
        return 1

    return ejecutar_gui(args.db)


if __name__ == "__main__":
    raise SystemExit(main())
