"""Componentes visuales reutilizables de la interfaz de OptiFiber."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import customtkinter as ctk

from src.presentacion.gui.tema import (
    ACENTO,
    ACENTO_FONDO,
    ACENTO_HOVER,
    ACENTO_TEXTO,
    ALERTA,
    BARRA_LATERAL,
    BORDE,
    BORDE_SUAVE,
    EXITO,
    FONDO_ALT,
    PANEL,
    PANEL_ALT,
    PANEL_HOVER,
    PELIGRO,
    PELIGRO_FONDO,
    RADIO_CONTROL,
    RADIO_PILDORA,
    RADIO_TARJETA,
    TEXTO,
    TEXTO_MEDIO,
    TEXTO_SUAVE,
    TEXTO_TENUE,
    fuente,
    mono,
)


def separador(maestro, color: str = BORDE_SUAVE, alto: int = 1) -> ctk.CTkFrame:
    """Linea horizontal sutil para separar bloques."""
    linea = ctk.CTkFrame(maestro, fg_color=color, height=alto, corner_radius=0)
    linea.pack(fill="x")
    return linea


class Tarjeta(ctk.CTkFrame):
    """Panel oscuro con borde suave, base de todas las secciones."""

    def __init__(self, maestro, **kwargs) -> None:
        kwargs.setdefault("fg_color", PANEL)
        kwargs.setdefault("corner_radius", RADIO_TARJETA)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", BORDE)
        super().__init__(maestro, **kwargs)


def cabecera_tarjeta(
    tarjeta,
    titulo: str,
    subtitulo: str | None = None,
    pildora: tuple[str, str, str] | None = None,
) -> ctk.CTkFrame:
    """Dibuja el encabezado de una tarjeta y devuelve su zona de acciones."""
    marco = ctk.CTkFrame(tarjeta, fg_color="transparent")
    marco.pack(fill="x", padx=20, pady=(16, 10))
    marco.grid_columnconfigure(0, weight=1)

    textos = ctk.CTkFrame(marco, fg_color="transparent")
    textos.grid(row=0, column=0, sticky="w")

    ctk.CTkLabel(
        textos,
        text=titulo,
        font=fuente(14, True),
        text_color=TEXTO,
        anchor="w",
    ).pack(anchor="w")
    if subtitulo:
        ctk.CTkLabel(
            textos,
            text=subtitulo,
            font=fuente(10),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

    acciones = ctk.CTkFrame(marco, fg_color="transparent", height=1)
    acciones.grid(row=0, column=1, sticky="e")

    if pildora:
        texto, color_texto, color_fondo = pildora
        Pildora(acciones, texto, color_texto, color_fondo).pack(side="right", padx=(8, 0))

    return acciones


class Pildora(ctk.CTkFrame):
    """Etiqueta compacta de color para estados, stock y conteos."""

    def __init__(
        self,
        maestro,
        texto: str,
        color_texto: str = TEXTO_MEDIO,
        color_fondo: str = PANEL_ALT,
        **kwargs,
    ) -> None:
        super().__init__(
            maestro,
            fg_color=color_fondo,
            corner_radius=RADIO_PILDORA,
            height=23,
            width=self._ancho(texto),
            **kwargs,
        )
        self.pack_propagate(False)
        self._label = ctk.CTkLabel(
            self,
            text=texto,
            font=fuente(9, True),
            text_color=color_texto,
            height=19,
        )
        self._label.pack(expand=True)

    @staticmethod
    def _ancho(texto: str) -> int:
        return max(46, int(len(texto) * 7.1) + 18)

    def actualizar(self, texto: str, color_texto: str, color_fondo: str) -> None:
        self.configure(fg_color=color_fondo, width=self._ancho(texto))
        self._label.configure(text=texto, text_color=color_texto)


def boton_primario(
    maestro,
    texto: str,
    comando: Callable | None = None,
    **kwargs,
) -> ctk.CTkButton:
    kwargs.setdefault("height", 38)
    kwargs.setdefault("corner_radius", RADIO_CONTROL)
    kwargs.setdefault("font", fuente(12, True))
    return ctk.CTkButton(
        maestro,
        text=texto,
        command=comando,
        fg_color=ACENTO,
        hover_color=ACENTO_HOVER,
        text_color=ACENTO_TEXTO,
        border_width=0,
        **kwargs,
    )


def boton_secundario(
    maestro,
    texto: str,
    comando: Callable | None = None,
    **kwargs,
) -> ctk.CTkButton:
    kwargs.setdefault("height", 38)
    kwargs.setdefault("corner_radius", RADIO_CONTROL)
    kwargs.setdefault("font", fuente(12, True))
    return ctk.CTkButton(
        maestro,
        text=texto,
        command=comando,
        fg_color="transparent",
        hover_color=PANEL_HOVER,
        text_color=TEXTO_MEDIO,
        border_width=1,
        border_color=BORDE,
        **kwargs,
    )


def boton_peligro(
    maestro,
    texto: str,
    comando: Callable | None = None,
    **kwargs,
) -> ctk.CTkButton:
    kwargs.setdefault("height", 38)
    kwargs.setdefault("corner_radius", RADIO_CONTROL)
    kwargs.setdefault("font", fuente(12, True))
    return ctk.CTkButton(
        maestro,
        text=texto,
        command=comando,
        fg_color="transparent",
        hover_color=PELIGRO_FONDO,
        text_color=PELIGRO,
        border_width=1,
        border_color="#5A2328",
        **kwargs,
    )


def boton_icono(
    maestro,
    texto: str,
    comando: Callable | None = None,
    **kwargs,
) -> ctk.CTkButton:
    kwargs.setdefault("width", 36)
    kwargs.setdefault("height", 36)
    kwargs.setdefault("corner_radius", RADIO_CONTROL)
    kwargs.setdefault("font", fuente(15))
    return ctk.CTkButton(
        maestro,
        text=texto,
        command=comando,
        fg_color="transparent",
        hover_color=PANEL_HOVER,
        text_color=TEXTO_MEDIO,
        border_width=1,
        border_color=BORDE,
        **kwargs,
    )


class Campo(ctk.CTkFrame):
    """Etiqueta + entrada de texto con foco resaltado."""

    def __init__(
        self,
        maestro,
        etiqueta: str,
        marcador: str = "",
        altura: int = 40,
    ) -> None:
        super().__init__(maestro, fg_color="transparent")
        ctk.CTkLabel(
            self,
            text=etiqueta,
            font=fuente(10, True),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(anchor="w", pady=(0, 5))
        self.entrada = ctk.CTkEntry(
            self,
            placeholder_text=marcador,
            placeholder_text_color=TEXTO_TENUE,
            height=altura,
            corner_radius=9,
            border_width=1,
            fg_color=FONDO_ALT,
            border_color=BORDE,
            text_color=TEXTO,
            font=fuente(12),
        )
        self.entrada.pack(fill="x")
        self.entrada.bind("<FocusIn>", lambda _evento: self._borde(ACENTO))
        self.entrada.bind("<FocusOut>", lambda _evento: self._borde(BORDE))

    def _borde(self, color: str) -> None:
        self.entrada.configure(border_color=color)

    def valor(self) -> str:
        return self.entrada.get().strip()

    def establecer(self, texto: str) -> None:
        self.entrada.delete(0, "end")
        self.entrada.insert(0, texto)

    def enfocar(self) -> None:
        self.entrada.focus_set()


class Selector(ctk.CTkFrame):
    """Etiqueta + menu desplegable oscuro."""

    def __init__(
        self,
        maestro,
        etiqueta: str,
        valores: list[str],
        comando: Callable | None = None,
        altura: int = 40,
    ) -> None:
        super().__init__(maestro, fg_color="transparent")
        ctk.CTkLabel(
            self,
            text=etiqueta,
            font=fuente(10, True),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(anchor="w", pady=(0, 5))
        self.menu = ctk.CTkOptionMenu(
            self,
            values=valores or ["Sin opciones"],
            command=comando,
            height=altura,
            corner_radius=9,
            fg_color=FONDO_ALT,
            button_color=PANEL_ALT,
            button_hover_color=PANEL_HOVER,
            text_color=TEXTO,
            font=fuente(12),
            dropdown_fg_color=PANEL,
            dropdown_hover_color=PANEL_HOVER,
            dropdown_text_color=TEXTO,
            dropdown_font=fuente(12),
            anchor="w",
        )
        self.menu.pack(fill="x")

    def valor(self) -> str:
        return self.menu.get()

    def establecer(self, valor: str) -> None:
        self.menu.set(valor)


@dataclass
class Columna:
    """Definicion de una columna para las tablas."""

    titulo: str
    peso: int = 0
    minimo: int = 80
    anchor: str = "w"


class Tabla(ctk.CTkFrame):
    """Cabecera fija y filas desplazables con columnas alineadas."""

    def __init__(
        self,
        maestro,
        columnas: list[Columna],
        altura: int = 380,
        **kwargs,
    ) -> None:
        super().__init__(maestro, fg_color="transparent", **kwargs)
        self.columnas = columnas
        self._indice = 0

        self._cabecera = ctk.CTkFrame(self, fg_color="transparent", height=30)
        self._cabecera.pack(fill="x", padx=(2, 14), pady=(0, 2))
        for indice, columna in enumerate(columnas):
            self._cabecera.grid_columnconfigure(
                indice,
                weight=columna.peso,
                minsize=columna.minimo,
            )
            ctk.CTkLabel(
                self._cabecera,
                text=columna.titulo.upper(),
                font=fuente(9, True),
                text_color=TEXTO_TENUE,
                anchor=columna.anchor,
            ).grid(row=0, column=indice, sticky="ew", padx=(10, 8), pady=(0, 6))

        self.cuerpo = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            height=altura,
            corner_radius=0,
            scrollbar_button_color="#1E293B",
            scrollbar_button_hover_color="#334155",
        )
        self.cuerpo.pack(fill="both", expand=True, padx=0, pady=0)

    def limpiar(self) -> None:
        for hijo in self.cuerpo.winfo_children():
            hijo.destroy()
        self._indice = 0

    def fila(self) -> FilaTabla:
        fila = FilaTabla(self.cuerpo, self.columnas, self._indice)
        fila.pack(fill="x", padx=2, pady=2)
        self._indice += 1
        return fila

    def vacio(self, mensaje: str, icono: str = "◌") -> None:
        marco = ctk.CTkFrame(self.cuerpo, fg_color=PANEL_ALT, corner_radius=12)
        marco.pack(fill="x", padx=2, pady=4)
        ctk.CTkLabel(
            marco,
            text=icono,
            font=fuente(24),
            text_color=TEXTO_TENUE,
        ).pack(pady=(26, 4))
        ctk.CTkLabel(
            marco,
            text=mensaje,
            font=fuente(11),
            text_color=TEXTO_SUAVE,
        ).pack(pady=(0, 28))


class FilaTabla(ctk.CTkFrame):
    """Fila de tabla: texto simple o un contenedor para pildoras y botones."""

    def __init__(self, maestro, columnas: list[Columna], indice: int) -> None:
        color = PANEL_ALT if indice % 2 == 0 else "#0D141C"
        super().__init__(maestro, fg_color=color, corner_radius=10)
        self.columnas = columnas
        for posicion, columna in enumerate(columnas):
            self.grid_columnconfigure(
                posicion,
                weight=columna.peso,
                minsize=columna.minimo,
            )

    def celda(
        self,
        indice: int,
        texto: object,
        color: str = TEXTO_MEDIO,
        font: tuple | None = None,
        anchor: str | None = None,
    ) -> ctk.CTkLabel:
        columna = self.columnas[indice]
        etiqueta = ctk.CTkLabel(
            self,
            text=str(texto),
            font=font or fuente(11),
            text_color=color,
            anchor=anchor or columna.anchor,
        )
        etiqueta.grid(
            row=0,
            column=indice,
            sticky="ew",
            padx=(10, 8),
            pady=6,
        )
        return etiqueta

    def contenedor(self, indice: int) -> ctk.CTkFrame:
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.grid(
            row=0,
            column=indice,
            sticky="ew",
            padx=(6, 8),
            pady=5,
        )
        return marco


class Modal(ctk.CTkToplevel):
    """Ventana modal oscura con cabecera propia y pie de acciones."""

    def __init__(
        self,
        maestro,
        titulo: str,
        subtitulo: str = "",
        ancho: int = 560,
        alto: int = 560,
        scrollable: bool = False,
    ) -> None:
        super().__init__(maestro)
        self.withdraw()
        self.overrideredirect(True)
        self.configure(fg_color="#05080C")
        self._maestro = maestro
        self._ancho = ancho
        self._alto = alto
        self._desplazamiento = (0, 0)

        marco = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=18,
            border_width=1,
            border_color=BORDE,
        )
        marco.pack(fill="both", expand=True)

        cabecera = ctk.CTkFrame(marco, fg_color="transparent")
        cabecera.pack(fill="x", padx=22, pady=(18, 12))
        cabecera.grid_columnconfigure(0, weight=1)

        textos = ctk.CTkFrame(cabecera, fg_color="transparent")
        textos.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            textos,
            text=titulo,
            font=fuente(17, True),
            text_color=TEXTO,
            anchor="w",
        ).pack(anchor="w")
        if subtitulo:
            ctk.CTkLabel(
                textos,
                text=subtitulo,
                font=fuente(10),
                text_color=TEXTO_SUAVE,
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))

        cerrar = ctk.CTkButton(
            cabecera,
            text="✕",
            width=30,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            hover_color=PELIGRO_FONDO,
            text_color=TEXTO_SUAVE,
            font=fuente(13),
            command=self.cerrar,
        )
        cerrar.grid(row=0, column=1, sticky="e")

        ctk.CTkFrame(marco, fg_color=BORDE_SUAVE, height=1).pack(fill="x", padx=20)

        if scrollable:
            self.cuerpo = ctk.CTkScrollableFrame(
                marco,
                fg_color="transparent",
                scrollbar_button_color="#1E293B",
                scrollbar_button_hover_color="#334155",
            )
        else:
            self.cuerpo = ctk.CTkFrame(marco, fg_color="transparent")
        self.cuerpo.pack(fill="both", expand=True, padx=22, pady=14)

        self.pie = ctk.CTkFrame(marco, fg_color="transparent")
        self.pie.pack(fill="x", padx=22, pady=(0, 18))

        self._error = ctk.CTkLabel(
            self.pie,
            text=" ",
            font=fuente(10, True),
            text_color=PELIGRO,
            anchor="w",
        )
        self._error.pack(fill="x", pady=(0, 4))

        self._acciones = ctk.CTkFrame(self.pie, fg_color="transparent")
        self._acciones.pack(fill="x")

        self._permitir_arrastre(cabecera)
        self.bind("<Escape>", lambda _evento: self.cerrar())

        self.update_idletasks()
        self._centrar()
        self.deiconify()
        self.transient(maestro)
        self.attributes("-topmost", True)
        self.after(100, self._activar)

    def _permitir_arrastre(self, widget) -> None:
        widget.bind("<ButtonPress-1>", self._iniciar_arrastre)
        widget.bind("<B1-Motion>", self._arrastrar)
        for hijo in widget.winfo_children():
            self._permitir_arrastre(hijo)

    def _iniciar_arrastre(self, evento) -> None:
        self._desplazamiento = (
            evento.x_root - self.winfo_x(),
            evento.y_root - self.winfo_y(),
        )

    def _arrastrar(self, evento) -> None:
        x = evento.x_root - self._desplazamiento[0]
        y = evento.y_root - self._desplazamiento[1]
        self.geometry(f"+{x}+{y}")

    def _centrar(self) -> None:
        self.update_idletasks()
        ancho_maestro = self._maestro.winfo_width()
        alto_maestro = self._maestro.winfo_height()
        ancho = min(self._ancho, self.winfo_screenwidth() - 40)
        alto = min(self._alto, self.winfo_screenheight() - 80)
        x = self._maestro.winfo_rootx() + max(0, (ancho_maestro - ancho) // 2)
        y = self._maestro.winfo_rooty() + max(0, (alto_maestro - alto) // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _activar(self) -> None:
        try:
            self.grab_set()
        except Exception:
            pass
        self.focus_force()

    def agregar_boton(
        self,
        texto: str,
        comando: Callable,
        tipo: str = "secundario",
    ) -> ctk.CTkButton:
        fabrica = {
            "primario": boton_primario,
            "peligro": boton_peligro,
        }.get(tipo, boton_secundario)
        boton = fabrica(self._acciones, texto, comando)
        boton.pack(side="right", padx=(8, 0))
        return boton

    def mostrar_error(self, mensaje: str) -> None:
        self._error.configure(text=mensaje if mensaje else " ")

    def limpiar_error(self) -> None:
        self._error.configure(text=" ")

    def cerrar(self) -> None:
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


class ModalConfirmacion(Modal):
    """Confirmacion breve para acciones destructivas o irreversibles."""

    def __init__(
        self,
        maestro,
        titulo: str,
        mensaje: str,
        texto_confirmar: str,
        comando: Callable,
        peligro: bool = True,
    ) -> None:
        super().__init__(maestro, titulo, ancho=480, alto=320)
        self._comando = comando
        self._peligro = peligro

        contenido = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        contenido.pack(fill="both", expand=True)

        color = PELIGRO if peligro else ACENTO
        fondo = PELIGRO_FONDO if peligro else ACENTO_FONDO
        icono = ctk.CTkFrame(contenido, fg_color=fondo, width=44, height=44, corner_radius=12)
        icono.pack(anchor="w", pady=(4, 12))
        icono.pack_propagate(False)
        ctk.CTkLabel(
            icono,
            text="!" if peligro else "✓",
            font=fuente(20, True),
            text_color=color,
        ).pack(expand=True)

        ctk.CTkLabel(
            contenido,
            text=mensaje,
            font=fuente(11),
            text_color=TEXTO_MEDIO,
            justify="left",
            anchor="w",
            wraplength=410,
        ).pack(fill="x")

        self.agregar_boton("Cancelar", self.cerrar)
        self.agregar_boton(
            texto_confirmar,
            self._ejecutar,
            "peligro" if peligro else "primario",
        )

    def _ejecutar(self) -> None:
        try:
            self._comando()
        except Exception as exc:
            self.mostrar_error(str(exc))
            return
        self.cerrar()


class Toast(ctk.CTkFrame):
    """Aviso flotante temporal en la esquina inferior derecha."""

    def __init__(self, maestro, texto: str, tipo: str = "exito") -> None:
        colores = {
            "exito": (EXITO, "#0C2A22"),
            "alerta": (ALERTA, "#2A2110"),
            "error": (PELIGRO, PELIGRO_FONDO),
            "info": ("#60A5FA", "#12213A"),
        }
        color, fondo = colores.get(tipo, (EXITO, "#0C2A22"))
        super().__init__(
            maestro,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=color,
        )
        barra = ctk.CTkFrame(self, fg_color=color, width=4, corner_radius=2)
        barra.pack(side="left", fill="y", padx=(0, 0))
        icono = {"exito": "✓", "alerta": "!", "error": "✕", "info": "i"}.get(tipo, "✓")
        ctk.CTkLabel(
            self,
            text=icono,
            font=fuente(13, True),
            text_color=color,
            width=22,
        ).pack(side="left", padx=(10, 2), pady=12)
        ctk.CTkLabel(
            self,
            text=texto,
            font=fuente(11, True),
            text_color=TEXTO,
            anchor="w",
        ).pack(side="left", padx=(0, 16), pady=12)
        self.place(relx=1.0, rely=1.0, x=-24, y=-20, anchor="se")
        self.lift()
        self.after(3200, self._cerrar)

    def _cerrar(self) -> None:
        if self.winfo_exists():
            self.destroy()


__all__ = [
    "BARRA_LATERAL",
    "Campo",
    "Columna",
    "FilaTabla",
    "Modal",
    "ModalConfirmacion",
    "Pildora",
    "Selector",
    "Tabla",
    "Tarjeta",
    "Toast",
    "boton_icono",
    "boton_peligro",
    "boton_primario",
    "boton_secundario",
    "cabecera_tarjeta",
    "mono",
    "separador",
]
