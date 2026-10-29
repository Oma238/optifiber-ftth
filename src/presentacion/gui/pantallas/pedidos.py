"""Pantalla de pedidos: punto de venta e historial de ventas."""

from __future__ import annotations

import customtkinter as ctk

from src.dominio.servicios import (
    ErrorDominio,
    calcular_descuento,
    calcular_subtotal,
    calcular_total_pedido,
)
from src.infraestructura.repositorios import ESTADOS_PEDIDO
from src.presentacion.gui.componentes import (
    Columna,
    Modal,
    Pildora,
    Selector,
    Tabla,
    Tarjeta,
    boton_icono,
    boton_primario,
    boton_secundario,
    cabecera_tarjeta,
)
from src.presentacion.gui.tema import (
    ACENTO,
    ACENTO_FONDO,
    ACENTO_TEXTO,
    BORDE,
    FONDO_ALT,
    PANEL,
    PANEL_ALT,
    PANEL_HOVER,
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
    iniciales,
    truncar,
)


class PantallaPedidos(ctk.CTkFrame):
    """Punto de venta con carrito y seguimiento de pedidos."""

    def __init__(
        self,
        maestro,
        app,
        modo: str = "nuevo",
        cliente_documento: str | None = None,
    ) -> None:
        super().__init__(maestro, fg_color="transparent", corner_radius=0)
        self.app = app
        self.modo = "nuevo"
        self.cliente_documento = cliente_documento
        self.carrito: dict[str, int] = {}
        self.cliente_sel = None
        self._productos = app.catalogo.listar_productos()
        self._por_sku = {producto.sku: producto for producto in self._productos}
        self._clientes = app.clientes.listar()
        if cliente_documento:
            self.cliente_sel = next(
                (cliente for cliente in self._clientes if cliente.documento == cliente_documento),
                None,
            )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._vista = None
        self._construir_barra()
        self.mostrar_vista(modo)

    def _construir_barra(self) -> None:
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        barra.grid_columnconfigure(0, weight=1)

        self._pista = ctk.CTkLabel(
            barra,
            text="Selecciona un cliente y arma el pedido",
            font=fuente(10),
            text_color=TEXTO_SUAVE,
            anchor="w",
        )
        self._pista.grid(row=0, column=0, sticky="w")

        segmento = ctk.CTkFrame(
            barra,
            fg_color=PANEL,
            corner_radius=11,
            border_width=1,
            border_color=BORDE,
        )
        segmento.grid(row=0, column=1, sticky="e")

        self._btn_nuevo = ctk.CTkButton(
            segmento,
            text="Nuevo pedido",
            command=lambda: self.mostrar_vista("nuevo"),
            width=112,
            height=30,
            corner_radius=8,
            font=fuente(10, True),
            border_width=0,
        )
        self._btn_nuevo.pack(side="left", padx=4, pady=4)

        self._btn_historial = ctk.CTkButton(
            segmento,
            text="Historial",
            command=lambda: self.mostrar_vista("historial"),
            width=100,
            height=30,
            corner_radius=8,
            font=fuente(10, True),
            border_width=0,
        )
        self._btn_historial.pack(side="left", padx=(0, 4), pady=4)

    def mostrar_vista(self, modo: str) -> None:
        self.modo = modo
        if self._vista is not None:
            self._vista.destroy()
        self._vista = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._vista.grid(row=1, column=0, sticky="nsew")

        if modo == "nuevo":
            self._pista.configure(
                text="Selecciona un cliente, agrega productos y confirma la venta"
            )
            self._vista_nuevo()
        else:
            self._pista.configure(text="Consulta el historial y actualiza el estado de cada pedido")
            self._vista_historial()

        self._pintar_modo()

    def _pintar_modo(self) -> None:
        for boton, modo in ((self._btn_nuevo, "nuevo"), (self._btn_historial, "historial")):
            activo = modo == self.modo
            boton.configure(
                fg_color=ACENTO if activo else "transparent",
                text_color=ACENTO_TEXTO if activo else TEXTO_SUAVE,
                hover_color="#5EEAD4" if activo else PANEL_HOVER,
            )

    def _vista_nuevo(self) -> None:
        self._vista.grid_columnconfigure(0, minsize=282, weight=0)
        self._vista.grid_columnconfigure(1, weight=1)
        self._vista.grid_columnconfigure(2, minsize=330, weight=0)
        self._vista.grid_rowconfigure(0, weight=1)

        self._tarjeta_cliente()
        self._tarjeta_productos()
        self._tarjeta_resumen()

    def _tarjeta_cliente(self) -> None:
        tarjeta = Tarjeta(self._vista)
        tarjeta.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        cabecera_tarjeta(tarjeta, "1 · Cliente", "Busca por nombre o documento")

        self._busqueda_clientes = ctk.CTkEntry(
            tarjeta,
            placeholder_text="Buscar cliente...",
            placeholder_text_color=TEXTO_TENUE,
            height=34,
            corner_radius=9,
            border_width=1,
            fg_color=FONDO_ALT,
            border_color=BORDE,
            text_color=TEXTO,
            font=fuente(10),
        )
        self._busqueda_clientes.pack(fill="x", padx=16, pady=(0, 8))
        self._busqueda_clientes.bind("<KeyRelease>", lambda _evento: self._render_clientes())

        self._lista_clientes = ctk.CTkScrollableFrame(
            tarjeta,
            fg_color="transparent",
            scrollbar_button_color="#1E293B",
            scrollbar_button_hover_color="#334155",
            height=280,
        )
        self._lista_clientes.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._render_clientes()

    def _render_clientes(self) -> None:
        for hijo in self._lista_clientes.winfo_children():
            hijo.destroy()

        texto = self._busqueda_clientes.get().strip().lower()
        visibles = [
            cliente
            for cliente in self._clientes
            if not texto
            or texto in cliente.nombre.lower()
            or texto in cliente.documento.lower()
        ]

        if not visibles:
            ctk.CTkLabel(
                self._lista_clientes,
                text="Sin coincidencias.",
                font=fuente(10),
                text_color=TEXTO_SUAVE,
            ).pack(pady=24)
            return

        for cliente in visibles:
            seleccionado = (
                self.cliente_sel is not None and self.cliente_sel.id == cliente.id
            )
            fila = ctk.CTkFrame(
                self._lista_clientes,
                fg_color=ACENTO_FONDO if seleccionado else PANEL_ALT,
                corner_radius=10,
                border_width=1,
                border_color=ACENTO if seleccionado else PANEL_ALT,
            )
            fila.pack(fill="x", pady=3)
            fila.grid_columnconfigure(0, weight=1)

            avatar = ctk.CTkFrame(
                fila,
                fg_color=ACENTO if seleccionado else "#1A2430",
                width=30,
                height=30,
                corner_radius=9,
            )
            avatar.grid(row=0, column=0, rowspan=2, sticky="w", padx=(10, 8), pady=8)
            avatar.grid_propagate(False)
            ctk.CTkLabel(
                avatar,
                text=iniciales(cliente.nombre),
                font=fuente(9, True),
                text_color=ACENTO_TEXTO if seleccionado else TEXTO_SUAVE,
            ).pack(expand=True)

            ctk.CTkLabel(
                fila,
                text=truncar(cliente.nombre, 24),
                font=fuente(10, True),
                text_color=TEXTO if seleccionado else TEXTO_MEDIO,
                anchor="w",
            ).grid(row=0, column=1, sticky="w", pady=(7, 0))
            ctk.CTkLabel(
                fila,
                text=f"DNI/RUC {cliente.documento}",
                font=mono(8),
                text_color=TEXTO_SUAVE,
                anchor="w",
            ).grid(row=1, column=1, sticky="w", pady=(0, 7))

            if seleccionado:
                ctk.CTkLabel(
                    fila,
                    text="✓",
                    font=fuente(12, True),
                    text_color=ACENTO,
                    width=18,
                ).grid(row=0, column=2, rowspan=2, padx=(0, 8))

            self._vincular_clic(fila, lambda c=cliente: self._seleccionar_cliente(c))

    def _vincular_clic(self, widget, comando) -> None:
        widget.bind("<Button-1>", lambda _evento: comando())
        for hijo in widget.winfo_children():
            self._vincular_clic(hijo, comando)

    def _seleccionar_cliente(self, cliente) -> None:
        self.cliente_sel = cliente
        self.cliente_documento = cliente.documento
        self._render_clientes()
        self._render_resumen()

    def _tarjeta_productos(self) -> None:
        tarjeta = Tarjeta(self._vista)
        tarjeta.grid(row=0, column=1, sticky="nsew", padx=(0, 12))
        acciones = cabecera_tarjeta(
            tarjeta,
            "2 · Productos",
            "Agrega unidades al pedido",
        )
        self._pildora_catalogo = Pildora(acciones, "0 productos", TEXTO_MEDIO, PANEL_ALT)
        self._pildora_catalogo.pack(side="right")

        self._busqueda_productos = ctk.CTkEntry(
            tarjeta,
            placeholder_text="Buscar por SKU o nombre...",
            placeholder_text_color=TEXTO_TENUE,
            height=34,
            corner_radius=9,
            border_width=1,
            fg_color=FONDO_ALT,
            border_color=BORDE,
            text_color=TEXTO,
            font=fuente(10),
        )
        self._busqueda_productos.pack(fill="x", padx=16, pady=(0, 8))
        self._busqueda_productos.bind("<KeyRelease>", lambda _evento: self._render_productos())

        self._lista_productos = ctk.CTkScrollableFrame(
            tarjeta,
            fg_color="transparent",
            scrollbar_button_color="#1E293B",
            scrollbar_button_hover_color="#334155",
            height=340,
        )
        self._lista_productos.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._render_productos()

    def _render_productos(self) -> None:
        for hijo in self._lista_productos.winfo_children():
            hijo.destroy()

        texto = self._busqueda_productos.get().strip().lower()
        visibles = [
            producto
            for producto in self._productos
            if not texto
            or texto in producto.nombre.lower()
            or texto in producto.sku.lower()
        ]

        if not visibles:
            ctk.CTkLabel(
                self._lista_productos,
                text="Sin productos que coincidan.",
                font=fuente(10),
                text_color=TEXTO_SUAVE,
            ).pack(pady=24)
        for producto in visibles:
            fila = ctk.CTkFrame(
                self._lista_productos,
                fg_color=PANEL_ALT,
                corner_radius=10,
            )
            fila.pack(fill="x", pady=3)
            fila.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                fila,
                text=truncar(producto.nombre, 32),
                font=fuente(10, True),
                text_color=TEXTO_MEDIO,
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))

            color_stock, _ = colores_stock(producto.stock)
            ctk.CTkLabel(
                fila,
                text=f"{producto.sku} · stock {producto.stock}",
                font=mono(8),
                text_color=color_stock,
                anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))

            ctk.CTkLabel(
                fila,
                text=formato_moneda(producto.precio),
                font=mono(10, True),
                text_color=TEXTO,
                anchor="e",
            ).grid(row=0, column=1, rowspan=2, padx=(6, 8))

            en_carrito = self.carrito.get(producto.sku, 0)
            disponible = producto.stock > 0 and en_carrito < producto.stock
            agregar = ctk.CTkButton(
                fila,
                text="+",
                command=lambda p=producto: self._agregar_producto(p),
                width=28,
                height=28,
                corner_radius=8,
                fg_color=ACENTO_FONDO if disponible else "#151D27",
                hover_color="#12302B",
                text_color=ACENTO if disponible else TEXTO_TENUE,
                font=fuente(14, True),
                border_width=0,
            )
            agregar.grid(row=0, column=2, rowspan=2, padx=(0, 10), pady=6)
            if not disponible:
                agregar.configure(state="disabled", text_color_disabled=TEXTO_TENUE)

        self._pildora_catalogo.actualizar(
            f"{len(self._productos)} productos",
            TEXTO_MEDIO,
            PANEL_ALT,
        )

    def _agregar_producto(self, producto) -> None:
        cantidad = self.carrito.get(producto.sku, 0)
        if cantidad >= producto.stock:
            self.app.notificar(
                f"No hay mas stock disponible de {producto.sku}.",
                "alerta",
            )
            return
        self.carrito[producto.sku] = cantidad + 1
        self._render_productos()
        self._render_resumen()

    def _cambiar_cantidad(self, sku: str, delta: int) -> None:
        producto = self._por_sku.get(sku)
        if producto is None:
            return
        cantidad = self.carrito.get(sku, 0) + delta
        if cantidad <= 0:
            self.carrito.pop(sku, None)
        elif cantidad > producto.stock:
            self.app.notificar(f"Stock insuficiente de {sku}.", "alerta")
            return
        else:
            self.carrito[sku] = cantidad
        self._render_productos()
        self._render_resumen()

    def _tarjeta_resumen(self) -> None:
        tarjeta = Tarjeta(self._vista)
        tarjeta.grid(row=0, column=2, sticky="nsew")
        cabecera_tarjeta(tarjeta, "3 · Resumen", "Revisa antes de confirmar")

        self._chip_cliente = ctk.CTkFrame(
            tarjeta,
            fg_color=FONDO_ALT,
            corner_radius=10,
            border_width=1,
            border_color=BORDE,
        )
        self._chip_cliente.pack(fill="x", padx=16, pady=(0, 10))

        self._lista_carrito = ctk.CTkScrollableFrame(
            tarjeta,
            fg_color="transparent",
            scrollbar_button_color="#1E293B",
            scrollbar_button_hover_color="#334155",
            height=230,
        )
        self._lista_carrito.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        totales = ctk.CTkFrame(tarjeta, fg_color="transparent")
        totales.pack(fill="x", padx=18, pady=(4, 8))
        totales.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            totales,
            text="Subtotal",
            font=fuente(10),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=2)
        self._lbl_subtotal = ctk.CTkLabel(
            totales,
            text=formato_moneda(0),
            font=mono(10),
            text_color=TEXTO_MEDIO,
            anchor="e",
        )
        self._lbl_subtotal.grid(row=0, column=1, sticky="e", pady=2)

        ctk.CTkLabel(
            totales,
            text="Descuento 5%",
            font=fuente(10),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=2)
        self._lbl_descuento = ctk.CTkLabel(
            totales,
            text="—",
            font=mono(10),
            text_color=TEXTO_SUAVE,
            anchor="e",
        )
        self._lbl_descuento.grid(row=1, column=1, sticky="e", pady=2)

        ctk.CTkFrame(totales, fg_color=BORDE, height=1).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=6,
        )

        ctk.CTkLabel(
            totales,
            text="Total a pagar",
            font=fuente(11, True),
            text_color=TEXTO,
            anchor="w",
        ).grid(row=3, column=0, sticky="w")
        self._lbl_total = ctk.CTkLabel(
            totales,
            text=formato_moneda(0),
            font=fuente(19, True),
            text_color=ACENTO,
            anchor="e",
        )
        self._lbl_total.grid(row=3, column=1, sticky="e")

        self._btn_confirmar = boton_primario(
            tarjeta,
            "Confirmar pedido",
            self._confirmar,
            height=42,
            font=fuente(12, True),
        )
        self._btn_confirmar.pack(fill="x", padx=16, pady=(6, 16))

        self._render_resumen()

    def _render_resumen(self) -> None:
        self._render_chip_cliente()
        self._render_carrito()

        lineas = []
        for sku, cantidad in self.carrito.items():
            producto = self._por_sku.get(sku)
            if producto is not None:
                lineas.append((cantidad, producto.precio))

        subtotal = sum(calcular_subtotal(cantidad, precio) for cantidad, precio in lineas)
        descuento = calcular_descuento(subtotal)
        total = calcular_total_pedido(lineas) if lineas else 0.0

        self._lbl_subtotal.configure(text=formato_moneda(subtotal))
        self._lbl_descuento.configure(
            text=formato_moneda(descuento) if descuento else "—",
            text_color=ACENTO if descuento else TEXTO_SUAVE,
        )
        self._lbl_total.configure(text=formato_moneda(total))
        self._btn_confirmar.configure(
            state="normal" if self.cliente_sel and self.carrito else "disabled",
            fg_color=ACENTO if self.cliente_sel and self.carrito else "#173B36",
            text_color=ACENTO_TEXTO if self.cliente_sel and self.carrito else TEXTO_SUAVE,
            text_color_disabled=TEXTO_SUAVE,
        )

    def _render_chip_cliente(self) -> None:
        for hijo in self._chip_cliente.winfo_children():
            hijo.destroy()

        if self.cliente_sel is None:
            ctk.CTkLabel(
                self._chip_cliente,
                text="Sin cliente seleccionado",
                font=fuente(10),
                text_color=TEXTO_SUAVE,
                anchor="w",
            ).pack(fill="x", padx=12, pady=10)
            return

        ctk.CTkLabel(
            self._chip_cliente,
            text="CLIENTE",
            font=fuente(8, True),
            text_color=TEXTO_TENUE,
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 0))
        ctk.CTkLabel(
            self._chip_cliente,
            text=truncar(self.cliente_sel.nombre, 28),
            font=fuente(10, True),
            text_color=TEXTO,
            anchor="w",
        ).pack(fill="x", padx=12)
        ctk.CTkLabel(
            self._chip_cliente,
            text=f"DNI/RUC {self.cliente_sel.documento}",
            font=mono(8),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(fill="x", padx=12, pady=(0, 8))

    def _render_carrito(self) -> None:
        for hijo in self._lista_carrito.winfo_children():
            hijo.destroy()

        if not self.carrito:
            ctk.CTkLabel(
                self._lista_carrito,
                text="◌",
                font=fuente(24),
                text_color=TEXTO_TENUE,
            ).pack(pady=(36, 2))
            ctk.CTkLabel(
                self._lista_carrito,
                text="El carrito esta vacio.",
                font=fuente(10),
                text_color=TEXTO_SUAVE,
            ).pack()
            return

        for sku, cantidad in self.carrito.items():
            producto = self._por_sku.get(sku)
            if producto is None:
                continue
            fila = ctk.CTkFrame(
                self._lista_carrito,
                fg_color=PANEL_ALT,
                corner_radius=10,
            )
            fila.pack(fill="x", pady=3)
            fila.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                fila,
                text=truncar(producto.nombre, 26),
                font=fuente(9, True),
                text_color=TEXTO_MEDIO,
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=(10, 4), pady=(8, 0))

            boton_icono(
                fila,
                "✕",
                lambda s=sku: self._quitar_producto(s),
                width=22,
                height=22,
                font=fuente(9),
            ).grid(row=0, column=2, padx=(0, 6), pady=(5, 0))

            controles = ctk.CTkFrame(fila, fg_color="transparent")
            controles.grid(row=1, column=0, sticky="w", padx=(10, 4), pady=(2, 8))

            ctk.CTkButton(
                controles,
                text="−",
                command=lambda s=sku: self._cambiar_cantidad(s, -1),
                width=22,
                height=22,
                corner_radius=6,
                fg_color="#18222E",
                hover_color="#202D3B",
                text_color=TEXTO_MEDIO,
                font=fuente(10, True),
                border_width=0,
            ).pack(side="left")
            ctk.CTkLabel(
                controles,
                text=str(cantidad),
                font=mono(9, True),
                text_color=TEXTO,
                width=26,
            ).pack(side="left")
            ctk.CTkButton(
                controles,
                text="+",
                command=lambda s=sku: self._cambiar_cantidad(s, 1),
                width=22,
                height=22,
                corner_radius=6,
                fg_color="#18222E",
                hover_color="#202D3B",
                text_color=ACENTO,
                font=fuente(10, True),
                border_width=0,
            ).pack(side="left")

            ctk.CTkLabel(
                fila,
                text=formato_moneda(calcular_subtotal(cantidad, producto.precio)),
                font=mono(9, True),
                text_color=TEXTO,
                anchor="e",
            ).grid(row=1, column=2, sticky="e", padx=(0, 8), pady=(0, 8))

    def _quitar_producto(self, sku: str) -> None:
        self.carrito.pop(sku, None)
        self._render_productos()
        self._render_resumen()

    def _confirmar(self) -> None:
        if self.cliente_sel is None:
            self.app.notificar("Selecciona un cliente antes de confirmar.", "alerta")
            return
        if not self.carrito:
            self.app.notificar("Agrega al menos un producto al pedido.", "alerta")
            return

        try:
            pedido = self.app.pedidos.crear_pedido(
                self.cliente_sel.documento,
                list(self.carrito.items()),
            )
        except (ErrorDominio, ValueError) as exc:
            self.app.notificar(str(exc), "error")
            return

        self.carrito.clear()
        self._productos = self.app.catalogo.listar_productos()
        self._por_sku = {producto.sku: producto for producto in self._productos}
        self.app.notificar(f"Pedido #{pedido.id:03d} registrado correctamente.")
        self.mostrar_vista("historial")
        ModalDetallePedido(self.app, self.app, pedido, self._render_historial)

    def _vista_historial(self) -> None:
        self._vista.grid_columnconfigure(0, weight=1)
        self._vista.grid_rowconfigure(1, weight=1)

        barra = ctk.CTkFrame(self._vista, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        barra.grid_columnconfigure(1, weight=1)

        self._filtro_estado = ctk.CTkOptionMenu(
            barra,
            values=["Todos los estados"] + sorted(ESTADOS_PEDIDO),
            command=lambda _valor: self._render_historial(),
            width=180,
            height=36,
            corner_radius=10,
            fg_color=FONDO_ALT,
            button_color=PANEL_ALT,
            button_hover_color=PANEL_HOVER,
            text_color=TEXTO_MEDIO,
            font=fuente(10, True),
            dropdown_fg_color=PANEL,
            dropdown_hover_color=PANEL_HOVER,
            dropdown_text_color=TEXTO,
            dropdown_font=fuente(11),
        )
        self._filtro_estado.grid(row=0, column=0, sticky="w")
        self._filtro_estado.set("Todos los estados")

        self._busqueda_historial = ctk.CTkEntry(
            barra,
            placeholder_text="Buscar por cliente o documento...",
            placeholder_text_color=TEXTO_TENUE,
            height=36,
            width=320,
            corner_radius=10,
            border_width=1,
            fg_color=FONDO_ALT,
            border_color=BORDE,
            text_color=TEXTO,
            font=fuente(10),
        )
        self._busqueda_historial.grid(row=0, column=1, sticky="w", padx=10)
        self._busqueda_historial.bind("<KeyRelease>", lambda _evento: self._render_historial())

        boton_primario(
            barra,
            "+  Nuevo pedido",
            lambda: self.mostrar_vista("nuevo"),
            height=36,
            font=fuente(10, True),
        ).grid(row=0, column=2, sticky="e")

        tarjeta = Tarjeta(self._vista)
        tarjeta.grid(row=1, column=0, sticky="nsew")
        acciones = cabecera_tarjeta(
            tarjeta,
            "Historial de pedidos",
            "Estado, cliente y monto de cada venta",
        )
        self._pildora_historial = Pildora(acciones, "0 pedidos", TEXTO_MEDIO, PANEL_ALT)
        self._pildora_historial.pack(side="right")

        self._tabla_historial = Tabla(
            tarjeta,
            [
                Columna("Pedido", minimo=70),
                Columna("Fecha", minimo=88),
                Columna("Cliente", peso=3, minimo=200),
                Columna("Documento", minimo=100),
                Columna("Estado", minimo=108),
                Columna("Total", minimo=96, anchor="e"),
                Columna("", minimo=56, anchor="center"),
            ],
            altura=390,
        )
        self._tabla_historial.pack(fill="both", expand=True, padx=16, pady=(0, 4))

        self._pie_historial = ctk.CTkLabel(
            tarjeta,
            text="",
            font=fuente(9),
            text_color=TEXTO_TENUE,
            anchor="w",
        )
        self._pie_historial.pack(fill="x", padx=22, pady=(0, 14))

        self._render_historial()

    def _render_historial(self) -> None:
        if not hasattr(self, "_tabla_historial"):
            return
        pedidos = self.app.pedidos.listar()
        filtro = self._filtro_estado.get()
        texto = self._busqueda_historial.get().strip().lower()

        visibles = []
        for pedido in pedidos:
            if filtro != "Todos los estados" and pedido.estado != filtro:
                continue
            contenido = f"{pedido.cliente.nombre} {pedido.cliente.documento}"
            if texto and texto not in contenido.lower():
                continue
            visibles.append(pedido)

        self._tabla_historial.limpiar()
        if not visibles:
            self._tabla_historial.vacio("No hay pedidos que coincidan con el filtro.", icono="▦")

        for pedido in visibles:
            fila = self._tabla_historial.fila()
            fila.celda(0, f"#{pedido.id:03d}", ACENTO, mono(10, True))
            fila.celda(1, formato_fecha(pedido.fecha), TEXTO_SUAVE, fuente(10))
            fila.celda(2, truncar(pedido.cliente.nombre, 28), TEXTO, fuente(10, True))
            fila.celda(3, pedido.cliente.documento, TEXTO_TENUE, mono(9))
            estado = fila.contenedor(4)
            color, fondo = colores_estado(pedido.estado)
            Pildora(estado, pedido.estado, color, fondo).pack(anchor="w")
            fila.celda(5, formato_moneda(pedido.total), TEXTO, mono(10, True), anchor="e")
            acciones = fila.contenedor(6)
            boton_secundario(
                acciones,
                "Ver",
                lambda p=pedido: ModalDetallePedido(self.app, self.app, p, self._render_historial),
                width=48,
                height=26,
                font=fuente(9, True),
            ).pack(anchor="center")

        total = sum(pedido.total for pedido in visibles)
        self._pildora_historial.actualizar(
            f"{len(visibles)} pedidos",
            TEXTO_MEDIO,
            PANEL_ALT,
        )
        self._pie_historial.configure(
            text=f"{len(visibles)} pedidos visibles · monto acumulado: {formato_moneda(total)}"
        )


class ModalDetallePedido(Modal):
    """Comprobante del pedido con cambio de estado."""

    def __init__(self, maestro, app, pedido, al_actualizar) -> None:
        super().__init__(
            maestro,
            f"Pedido #{pedido.id:03d}",
            f"{formato_fecha(pedido.fecha)} · {pedido.cliente.nombre}",
            ancho=660,
            alto=840,
            scrollable=True,
        )
        self.app = app
        self.pedido = app.pedidos.obtener(pedido.id) or pedido
        self.al_actualizar = al_actualizar

        hero = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        hero.pack(fill="x", pady=(0, 14))
        hero.grid_columnconfigure(0, weight=1)

        cliente = ctk.CTkFrame(hero, fg_color="transparent")
        cliente.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            cliente,
            text=self.pedido.cliente.nombre,
            font=fuente(14, True),
            text_color=TEXTO,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            cliente,
            text=f"DNI/RUC {self.pedido.cliente.documento}",
            font=mono(9),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        color, fondo = colores_estado(self.pedido.estado)
        self._pildora_estado = Pildora(hero, self.pedido.estado, color, fondo)
        self._pildora_estado.grid(row=0, column=1, sticky="e")

        contacto = ctk.CTkFrame(self.cuerpo, fg_color=PANEL_ALT, corner_radius=11)
        contacto.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(
            contacto,
            text=f"Telefono: {self.pedido.cliente.telefono or '—'}",
            font=fuente(9),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(side="left", padx=12, pady=9)
        ctk.CTkLabel(
            contacto,
            text=truncar(self.pedido.cliente.email or "Sin correo", 30),
            font=fuente(9),
            text_color=TEXTO_SUAVE,
            anchor="e",
        ).pack(side="right", padx=12, pady=9)

        ctk.CTkLabel(
            self.cuerpo,
            text="DETALLE DEL PEDIDO",
            font=fuente(9, True),
            text_color=TEXTO_TENUE,
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        subtotal = 0.0
        for detalle in self.pedido.detalles:
            subtotal += detalle.subtotal
            fila = ctk.CTkFrame(self.cuerpo, fg_color=PANEL_ALT, corner_radius=10)
            fila.pack(fill="x", pady=3)
            fila.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                fila,
                text=truncar(detalle.producto.nombre, 38),
                font=fuente(10, True),
                text_color=TEXTO_MEDIO,
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))
            ctk.CTkLabel(
                fila,
                text=(
                    f"{detalle.producto.sku} · {detalle.cantidad} x "
                    f"{formato_moneda(detalle.precio_unitario)}"
                ),
                font=mono(8),
                text_color=TEXTO_SUAVE,
                anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))
            ctk.CTkLabel(
                fila,
                text=formato_moneda(detalle.subtotal),
                font=mono(10, True),
                text_color=TEXTO,
                anchor="e",
            ).grid(row=0, column=1, rowspan=2, sticky="e", padx=12)

        totales = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        totales.pack(fill="x", pady=(14, 12))
        totales.grid_columnconfigure(1, weight=1)

        descuento = round(subtotal - self.pedido.total, 2)
        filas = [
            ("Subtotal", formato_moneda(subtotal), TEXTO_MEDIO),
            (
                "Descuento por volumen",
                f"-{formato_moneda(descuento)}" if descuento else "—",
                ACENTO,
            ),
        ]
        for indice, (etiqueta, valor, color_valor) in enumerate(filas):
            ctk.CTkLabel(
                totales,
                text=etiqueta,
                font=fuente(10),
                text_color=TEXTO_SUAVE,
                anchor="w",
            ).grid(row=indice, column=0, sticky="w", pady=2)
            ctk.CTkLabel(
                totales,
                text=valor,
                font=mono(10, True),
                text_color=color_valor,
                anchor="e",
            ).grid(row=indice, column=1, sticky="e", pady=2)

        ctk.CTkFrame(totales, fg_color=BORDE, height=1).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=6,
        )
        ctk.CTkLabel(
            totales,
            text="Total del pedido",
            font=fuente(11, True),
            text_color=TEXTO,
            anchor="w",
        ).grid(row=3, column=0, sticky="w")
        ctk.CTkLabel(
            totales,
            text=formato_moneda(self.pedido.total),
            font=fuente(19, True),
            text_color=ACENTO,
            anchor="e",
        ).grid(row=3, column=1, sticky="e")

        ctk.CTkLabel(
            self.cuerpo,
            text="ESTADO DEL PEDIDO",
            font=fuente(9, True),
            text_color=TEXTO_TENUE,
            anchor="w",
        ).pack(fill="x", pady=(6, 6))

        controles = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        controles.pack(fill="x")
        self._selector_estado = Selector(
            controles,
            "Nuevo estado",
            sorted(ESTADOS_PEDIDO),
        )
        self._selector_estado.pack(side="left", fill="x", expand=True)
        self._selector_estado.establecer(self.pedido.estado)

        boton_primario(
            controles,
            "Actualizar",
            self._actualizar_estado,
            height=40,
            font=fuente(10, True),
        ).pack(side="left", padx=(10, 0), pady=(18, 0))

        self.agregar_boton("Cerrar", self.cerrar)

    def _actualizar_estado(self) -> None:
        nuevo = self._selector_estado.valor()
        if nuevo == self.pedido.estado:
            self.app.notificar("El pedido ya tiene ese estado.", "info")
            return
        try:
            self.pedido = self.app.pedidos.cambiar_estado(self.pedido.id, nuevo)
        except (ErrorDominio, ValueError) as exc:
            self.app.notificar(str(exc), "error")
            return

        color, fondo = colores_estado(self.pedido.estado)
        self._pildora_estado.actualizar(self.pedido.estado, color, fondo)
        self.al_actualizar()
        self.app.notificar(f"Pedido #{self.pedido.id:03d} actualizado a {self.pedido.estado}.")
