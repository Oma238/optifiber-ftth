"""Punto de entrada de OptiFiber FTTH.

Uso:
    python -m src.main            # menu interactivo
    python -m src.main --demo     # demostracion automatica en memoria
"""

from src.presentacion.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
