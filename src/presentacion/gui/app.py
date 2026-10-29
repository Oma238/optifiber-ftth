"""Aplicacion de escritorio de OptiFiber con navegacion por pantallas."""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
from sqlalchemy.orm import Session

from src.infraestructura.db import (
    crear_engine,
    crear_session_factory,
    inicializar_db,
)
from src.infraestructura.repositorios import (
    CatalogoRepositorio,
    ClienteRepositorio,
    PedidoRepositorio,
)
from src.infraestructura.seed import sembrar_datos, sembrar_pedidos_demo
from src.presentacion.gui.componentes import Toast, boton_icono
from src.presentacion.gui.pantallas import (
    PantallaCatalogo,
    PantallaClientes,
    PantallaDashboard,
    PantallaPedidos,
    PantallaReportes,
)
from src.presentacion.gui.tema import (
    ACENTO,
    ACENTO_FONDO,
    BARRA_LATERAL,
    BORDE,
    BORDE_SUAVE,
    EXITO,
    FONDO,
    PANEL,
    TEXTO,
    TEXTO_MEDIO,
    TEXTO_SUAVE,
    TEXTO_TENUE,
    fuente,
)
from src.presentacion.gui.utilidades import fecha_larga, truncar

RAIZ_PROYECTO = Path(__file__).resolve().parents[3]
RUTA_ICONO = RAIZ_PROYECTO / "assets" / "optifiber.ico"

NAVEGACION = [
    ("dashboard", "Panel general", "◫"),
    ("catalogo", "Catalogo", "▤"),
    ("clientes", "Clientes", "◍"),
    ("pedidos", "Pedidos", "▦"),
    ("reportes", "Reportes", "◔"),
]

TITULOS = {
    "dashboard": ("Panel general", "Resumen de la operacion FTTH de OptiFiber"),
    "catalogo": ("Catalogo", "Productos, categorias y etiquetas del inventario"),
    "clientes": ("Clientes", "Directorio, contacto e historial de compras"),
    "pedidos": ("Pedidos", "Registro de ventas y seguimiento de estados"),
    "reportes": ("Reportes", "Indicadores comerciales y salud del inventario"),
}


class BarraLateral(ctk.CTkFrame):
    """Navegacion fija con identidad de marca y estado de la base local."""

    def __init__(self, maestro, app: AplicacionOptiFiber) -> None:
        super().__init__(maestro, fg_color=BARRA_LATERAL, width=232, corner_radius=0)
        self.app = app
        self._botones: dict[str, ctk.CTkButton] = {}

        marca = ctk.CTkFrame(self, fg_color="transparent")
        marca.pack(fill="x", padx=18, pady=(24, 22))

        icono = ctk.CTkFrame(marca, fg_color=ACENTO, width=36, height=36, corner_radius=11)
        icono.pack(side="left")
        icono.pack_propagate(False)
        ctk.CTkLabel(
            icono,
            text="O",
            font=fuente(19, True),
            text_color="#04231F",
        ).pack(expand=True)

        textos = ctk.CTkFrame(marca, fg_color="transparent")
        textos.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            textos,
            text="OPTIFIBER",
            font=fuente(15, True),
            text_color=TEXTO,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            textos,
            text="Gestion FTTH",
            font=fuente(9),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkFrame(self, fg_color=BORDE_SUAVE, height=1).pack(fill="x", padx=18)

        ctk.CTkLabel(
            self,
            text="OPERACION",
            font=fuente(8, True),
            text_color=TEXTO_TENUE,
            anchor="w",
        ).pack(fill="x", padx=22, pady=(20, 8))

        for clave, titulo, icono_texto in NAVEGACION:
            boton = ctk.CTkButton(
                self,
                text=f"{icono_texto}   {titulo}",
                command=lambda c=clave: self.app.mostrar(c),
                height=42,
                corner_radius=10,
                anchor="w",
                font=fuente(12, True),
                fg_color="transparent",
                hover_color="#121A24",
                text_color=TEXTO_SUAVE,
                border_width=0,
            )
            boton.pack(fill="x", padx=14, pady=2)
            self._botones[clave] = boton

        pie = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=BORDE,
        )
        pie.pack(side="bottom", fill="x", padx=14, pady=16)

        estado = ctk.CTkFrame(pie, fg_color="transparent")
        estado.pack(fill="x", padx=12, pady=(12, 4))
        ctk.CTkLabel(
            estado,
            text="●",
            font=fuente(9),
            text_color=EXITO,
            width=12,
        ).pack(side="left")
        ctk.CTkLabel(
            estado,
            text="SQLite local",
            font=fuente(10, True),
            text_color=TEXTO_MEDIO,
            anchor="w",
        ).pack(side="left", padx=(3, 0))

        ctk.CTkLabel(
            pie,
            text=truncar(app.nombre_db, 26),
            font=fuente(9),
            text_color=TEXTO_TENUE,
            anchor="w",
        ).pack(fill="x", padx=12)

        ctk.CTkLabel(
            pie,
            text="v1.1 · Interfaz grafica",
            font=fuente(8),
            text_color=TEXTO_TENUE,
            anchor="w",
        ).pack(fill="x", padx=12, pady=(2, 12))

    def marcar(self, clave: str) -> None:
        for nombre, boton in self._botones.items():
            activo = nombre == clave
            boton.configure(
                fg_color=ACENTO_FONDO if activo else "transparent",
                text_color=ACENTO if activo else TEXTO_SUAVE,
                hover_color="#12302B" if activo else "#121A24",
            )


class BarraSuperior(ctk.CTkFrame):
    """Titulo contextual, fecha y accion de actualizacion."""

    def __init__(self, maestro, app: AplicacionOptiFiber) -> None:
        super().__init__(maestro, fg_color="transparent", height=78, corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        textos = ctk.CTkFrame(self, fg_color="transparent")
        textos.grid(row=0, column=0, sticky="w", padx=28, pady=(18, 12))
        self.titulo = ctk.CTkLabel(
            textos,
            text="Panel general",
            font=fuente(22, True),
            text_color=TEXTO,
            anchor="w",
        )
        self.titulo.pack(anchor="w")
        self.subtitulo = ctk.CTkLabel(
            textos,
            text="",
            font=fuente(10),
            text_color=TEXTO_SUAVE,
            anchor="w",
        )
        self.subtitulo.pack(anchor="w", pady=(2, 0))

        derecha = ctk.CTkFrame(self, fg_color="transparent")
        derecha.grid(row=0, column=1, sticky="e", padx=28, pady=(18, 12))

        fecha = ctk.CTkFrame(
            derecha,
            fg_color=PANEL,
            corner_radius=10,
            border_width=1,
            border_color=BORDE,
        )
        fecha.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            fecha,
            text="▦",
            font=fuente(11),
            text_color=TEXTO_TENUE,
        ).pack(side="left", padx=(10, 4), pady=7)
        ctk.CTkLabel(
            fecha,
            text=fecha_larga(),
            font=fuente(10),
            text_color=TEXTO_SUAVE,
        ).pack(side="left", padx=(0, 12), pady=7)

        boton_icono(
            derecha,
            "↻",
            app.refrescar,
            width=36,
            height=36,
        ).pack(side="left")

        ctk.CTkFrame(maestro, fg_color=BORDE_SUAVE, height=1, corner_radius=0).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
        )

    def actualizar(self, clave: str) -> None:
        titulo, subtitulo = TITULOS[clave]
        self.titulo.configure(text=titulo)
        self.subtitulo.configure(text=subtitulo)


class AplicacionOptiFiber(ctk.CTk):
    """Ventana principal: sesion SQLAlchemy, navegacion y avisos."""

    def __init__(self, db_url: str | None = None) -> None:
        ctk.set_appearance_mode("dark")
        super().__init__(fg_color=FONDO)
        self.title("OptiFiber · Gestion FTTH")
        self.minsize(1180, 720)
        self._centrar_ventana(1360, 860)
        self._aplicar_icono()

        self.engine = crear_engine(db_url)
        inicializar_db(self.engine)
        self.session: Session = crear_session_factory(self.engine)()
        sembrar_datos(self.session)
        sembrar_pedidos_demo(self.session)

        self.clientes = ClienteRepositorio(self.session)
        self.catalogo = CatalogoRepositorio(self.session)
        self.pedidos = PedidoRepositorio(self.session)

        self.nombre_db = self._nombre_base()
        self._clave = "dashboard"
        self._pantalla = None
        self._aviso: Toast | None = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.barra_lateral = BarraLateral(self, self)
        self.barra_lateral.grid(row=0, column=0, sticky="ns")

        principal = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        principal.grid(row=0, column=1, sticky="nsew")
        principal.grid_rowconfigure(1, weight=1)
        principal.grid_columnconfigure(0, weight=1)

        self.barra_superior = BarraSuperior(principal, self)
        self.barra_superior.grid(row=0, column=0, sticky="ew")

        self.contenido = ctk.CTkFrame(principal, fg_color="transparent", corner_radius=0)
        self.contenido.grid(row=1, column=0, sticky="nsew", padx=28, pady=(18, 22))
        self.contenido.grid_rowconfigure(0, weight=1)
        self.contenido.grid_columnconfigure(0, weight=1)

        self._pantallas = {
            "dashboard": PantallaDashboard,
            "catalogo": PantallaCatalogo,
            "clientes": PantallaClientes,
            "pedidos": PantallaPedidos,
            "reportes": PantallaReportes,
        }

        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self.bind("<F5>", lambda _evento: self.refrescar())
        for indice, clave in enumerate(self._pantallas, start=1):
            self.bind(
                f"<Control-Key-{indice}>",
                lambda _evento, c=clave: self.mostrar(c),
            )

        self.mostrar("dashboard")
        self.after(120, self._enfocar)

    def _centrar_ventana(self, ancho: int, alto: int) -> None:
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        ancho = min(ancho, ancho_pantalla - 60)
        alto = min(alto, alto_pantalla - 80)
        x = max(0, (ancho_pantalla - ancho) // 2)
        y = max(0, (alto_pantalla - alto) // 2 - 10)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _aplicar_icono(self) -> None:
        if RUTA_ICONO.exists():
            try:
                self.iconbitmap(str(RUTA_ICONO))
            except Exception:
                pass

    def _nombre_base(self) -> str:
        base = self.engine.url.database
        if not base or base == ":memory:":
            return "memoria temporal"
        return Path(base).name

    def _enfocar(self) -> None:
        self.lift()
        self.focus_force()

    def mostrar(self, clave: str, **kwargs) -> None:
        """Cambia de pantalla destruyendo la anterior."""
        if clave not in self._pantallas:
            return
        if self._pantalla is not None:
            self._pantalla.destroy()
        pantalla = self._pantallas[clave](self.contenido, self, **kwargs)
        pantalla.grid(row=0, column=0, sticky="nsew")
        self._pantalla = pantalla
        self._clave = clave
        self.barra_superior.actualizar(clave)
        self.barra_lateral.marcar(clave)

    def refrescar(self) -> None:
        self.mostrar(self._clave)

    def ir_a(self, clave: str, **kwargs) -> None:
        self.mostrar(clave, **kwargs)

    def notificar(self, texto: str, tipo: str = "exito") -> None:
        if self._aviso is not None and self._aviso.winfo_exists():
            self._aviso.destroy()
        self._aviso = Toast(self, texto, tipo)

    def _cerrar(self) -> None:
        try:
            self.session.close()
        finally:
            self.engine.dispose()
            self.destroy()


def ejecutar_gui(db_url: str | None = None) -> int:
    """Inicia la aplicacion de escritorio."""
    app = AplicacionOptiFiber(db_url)
    app.mainloop()
    return 0


__all__ = ["AplicacionOptiFiber", "ejecutar_gui"]
