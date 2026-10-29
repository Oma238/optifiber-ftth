"""Pantalla de resumen general de OptiFiber."""

from __future__ import annotations

import customtkinter as ctk

from src.presentacion.gui.componentes import (
    Pildora,
    Tarjeta,
    boton_primario,
    boton_secundario,
    cabecera_tarjeta,
)
from src.presentacion.gui.tema import (
    ACENTO,
    ACENTO_FONDO,
    ALERTA,
    ALERTA_FONDO,
    BORDE,
    INFO,
    INFO_FONDO,
    MORADO,
    MORADO_FONDO,
    PANEL,
    PANEL_ALT,
    TEXTO,
    TEXTO_MEDIO,
    TEXTO_SUAVE,
    TEXTO_TENUE,
    fuente,
    mono,
)
from src.presentacion.gui.utilidades import (
    colores_estado,
    colores_stock,
    formato_fecha,
    formato_moneda,
    truncar,
)


class TarjetaKPI(ctk.CTkFrame):
    """Indicador compacto con etiqueta, cifra y contexto."""

    def __init__(
        self,
        maestro,
        etiqueta: str,
        valor: str,
        pista: str,
        color: str,
        fondo: str,
        icono: str,
    ) -> None:
        super().__init__(
            maestro,
            fg_color=PANEL,
            corner_radius=16,
            border_width=1,
            border_color=BORDE,
        )
        superior = ctk.CTkFrame(self, fg_color="transparent")
        superior.pack(fill="x", padx=18, pady=(16, 2))

        chip = ctk.CTkFrame(superior, fg_color=fondo, width=26, height=26, corner_radius=8)
        chip.pack(side="left")
        chip.pack_propagate(False)
        ctk.CTkLabel(chip, text=icono, font=fuente(12, True), text_color=color).pack(expand=True)

        ctk.CTkLabel(
            superior,
            text=etiqueta.upper(),
            font=fuente(8, True),
            text_color=TEXTO_TENUE,
            anchor="w",
        ).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            self,
            text=valor,
            font=fuente(23, True),
            text_color=TEXTO,
            anchor="w",
        ).pack(fill="x", padx=18, pady=(6, 0))

        ctk.CTkLabel(
            self,
            text=pista,
            font=fuente(9),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(fill="x", padx=18, pady=(1, 16))


class PantallaDashboard(ctk.CTkFrame):
    """Vista inicial: KPIs, pedidos recientes y stock critico."""

    def __init__(self, maestro, app) -> None:
        super().__init__(maestro, fg_color="transparent", corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        pedidos = app.pedidos.listar()
        activos = [pedido for pedido in pedidos if pedido.estado != "CANCELADO"]
        ingresos = sum(pedido.total for pedido in activos)
        clientes = app.clientes.listar()
        productos = app.catalogo.listar_productos()

        kpis = ctk.CTkFrame(self, fg_color="transparent")
        kpis.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for indice in range(4):
            kpis.grid_columnconfigure(indice, weight=1)

        TarjetaKPI(
            kpis,
            "Ingresos",
            formato_moneda(ingresos),
            "Facturacion registrada",
            ACENTO,
            ACENTO_FONDO,
            "↗",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))
        TarjetaKPI(
            kpis,
            "Pedidos",
            str(len(pedidos)),
            "Ordenes en el historial",
            INFO,
            INFO_FONDO,
            "▦",
        ).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        TarjetaKPI(
            kpis,
            "Clientes",
            str(len(clientes)),
            "Contactos registrados",
            MORADO,
            MORADO_FONDO,
            "◍",
        ).grid(row=0, column=2, sticky="ew", padx=(0, 10))
        TarjetaKPI(
            kpis,
            "Productos",
            str(len(productos)),
            "Referencias activas",
            ALERTA,
            ALERTA_FONDO,
            "▤",
        ).grid(row=0, column=3, sticky="ew")

        paneles = ctk.CTkFrame(self, fg_color="transparent")
        paneles.grid(row=1, column=0, sticky="nsew")
        paneles.grid_rowconfigure(0, weight=1)
        paneles.grid_columnconfigure(0, weight=3)
        paneles.grid_columnconfigure(1, weight=2)

        self._pedidos_recientes(paneles, pedidos)
        self._stock_bajo(paneles, app.catalogo.stock_bajo(limite=5))

    def _pedidos_recientes(self, maestro, pedidos) -> None:
        tarjeta = Tarjeta(maestro)
        tarjeta.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        acciones = cabecera_tarjeta(
            tarjeta,
            "Pedidos recientes",
            "Ultimos movimientos registrados",
        )
        boton_secundario(
            acciones,
            "Ver historial",
            lambda: self.app.ir_a("pedidos", modo="historial"),
            height=30,
            font=fuente(10, True),
        ).pack(side="right")

        cuerpo = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        if not pedidos:
            self._vacio(cuerpo, "Aun no hay pedidos registrados.")
            boton_primario(
                cuerpo,
                "Registrar el primer pedido",
                lambda: self.app.ir_a("pedidos"),
                height=34,
            ).pack(pady=(0, 10))
            return

        for pedido in pedidos[:5]:
            fila = ctk.CTkFrame(cuerpo, fg_color=PANEL_ALT, corner_radius=11)
            fila.pack(fill="x", pady=3)
            fila.grid_columnconfigure(0, weight=1)

            izquierda = ctk.CTkFrame(fila, fg_color="transparent")
            izquierda.grid(row=0, column=0, sticky="w", padx=14, pady=9)
            ctk.CTkLabel(
                izquierda,
                text=f"#{pedido.id:03d}  {truncar(pedido.cliente.nombre, 30)}",
                font=fuente(11, True),
                text_color=TEXTO,
                anchor="w",
            ).pack(anchor="w")
            ctk.CTkLabel(
                izquierda,
                text=f"{formato_fecha(pedido.fecha)} · {truncar(pedido.cliente.documento, 16)}",
                font=fuente(9),
                text_color=TEXTO_TENUE,
                anchor="w",
            ).pack(anchor="w")

            color, fondo = colores_estado(pedido.estado)
            Pildora(fila, pedido.estado, color, fondo).grid(
                row=0,
                column=1,
                padx=10,
            )

            ctk.CTkLabel(
                fila,
                text=formato_moneda(pedido.total),
                font=mono(11, True),
                text_color=TEXTO,
                anchor="e",
            ).grid(row=0, column=2, sticky="e", padx=(0, 14))

    def _stock_bajo(self, maestro, productos) -> None:
        tarjeta = Tarjeta(maestro)
        tarjeta.grid(row=0, column=1, sticky="nsew")
        acciones = cabecera_tarjeta(
            tarjeta,
            "Stock bajo",
            "Productos con 5 unidades o menos",
            (str(len(productos)), ALERTA, ALERTA_FONDO),
        )
        boton_secundario(
            acciones,
            "Catalogo",
            lambda: self.app.ir_a("catalogo"),
            height=30,
            font=fuente(10, True),
        ).pack(side="right")

        cuerpo = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        if not productos:
            self._vacio(
                cuerpo,
                "Todo el inventario tiene stock suficiente.",
                icono="✓",
            )
            return

        for producto in productos[:6]:
            fila = ctk.CTkFrame(cuerpo, fg_color=PANEL_ALT, corner_radius=11)
            fila.pack(fill="x", pady=3)
            fila.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                fila,
                text=truncar(producto.nombre, 30),
                font=fuente(10, True),
                text_color=TEXTO_MEDIO,
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))
            ctk.CTkLabel(
                fila,
                text=producto.sku,
                font=mono(9),
                text_color=TEXTO_TENUE,
                anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))

            color, fondo = colores_stock(producto.stock)
            Pildora(fila, f"{producto.stock} und.", color, fondo).grid(
                row=0,
                column=1,
                rowspan=2,
                padx=(8, 12),
            )

    @staticmethod
    def _vacio(marco, mensaje: str, icono: str = "◌") -> None:
        ctk.CTkLabel(
            marco,
            text=icono,
            font=fuente(26),
            text_color=TEXTO_TENUE,
        ).pack(pady=(30, 2))
        ctk.CTkLabel(
            marco,
            text=mensaje,
            font=fuente(10),
            text_color=TEXTO_SUAVE,
        ).pack(pady=(0, 10))
