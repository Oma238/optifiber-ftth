"""Pantalla de catalogo: productos, categorias y etiquetas."""

from __future__ import annotations

import customtkinter as ctk

from src.dominio.servicios import ErrorDominio
from src.presentacion.gui.componentes import (
    Campo,
    Columna,
    Modal,
    Pildora,
    Selector,
    Tabla,
    Tarjeta,
    boton_primario,
    boton_secundario,
    cabecera_tarjeta,
)
from src.presentacion.gui.tema import (
    ACENTO,
    BORDE,
    FONDO_ALT,
    PANEL_ALT,
    TEXTO,
    TEXTO_MEDIO,
    TEXTO_SUAVE,
    TEXTO_TENUE,
    fuente,
    mono,
)
from src.presentacion.gui.utilidades import (
    colores_stock,
    formato_moneda,
    truncar,
)


class PantallaCatalogo(ctk.CTkFrame):
    """Inventario FTTH con busqueda, filtro por categoria y alta de productos."""

    def __init__(self, maestro, app) -> None:
        super().__init__(maestro, fg_color="transparent", corner_radius=0)
        self.app = app
        self._filtro = "Todas las categorias"
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir_barra()
        self._construir_tarjeta()
        self.recargar()

    def _construir_barra(self) -> None:
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        barra.grid_columnconfigure(0, weight=1)

        self.busqueda = ctk.CTkEntry(
            barra,
            placeholder_text="Buscar por SKU, nombre o etiqueta...",
            placeholder_text_color=TEXTO_TENUE,
            height=38,
            width=380,
            corner_radius=10,
            border_width=1,
            fg_color=FONDO_ALT,
            border_color=BORDE,
            text_color=TEXTO,
            font=fuente(11),
        )
        self.busqueda.grid(row=0, column=0, sticky="w")
        self.busqueda.bind("<KeyRelease>", lambda _evento: self._render_tabla())

        self.filtro = ctk.CTkOptionMenu(
            barra,
            values=["Todas las categorias"],
            command=self._cambiar_filtro,
            width=190,
            height=38,
            corner_radius=10,
            fg_color=FONDO_ALT,
            button_color=PANEL_ALT,
            button_hover_color="#16202C",
            text_color=TEXTO_MEDIO,
            font=fuente(10, True),
            dropdown_fg_color="#0E151E",
            dropdown_hover_color="#16202C",
            dropdown_text_color=TEXTO,
            dropdown_font=fuente(11),
        )
        self.filtro.grid(row=0, column=1, padx=(10, 8))

        boton_secundario(
            barra,
            "Nueva categoria",
            self._abrir_categoria,
            height=38,
            font=fuente(11, True),
        ).grid(row=0, column=2, padx=(0, 8))

        boton_primario(
            barra,
            "+  Nuevo producto",
            self._abrir_producto,
            height=38,
            font=fuente(11, True),
        ).grid(row=0, column=3)

    def _construir_tarjeta(self) -> None:
        tarjeta = Tarjeta(self)
        tarjeta.grid(row=1, column=0, sticky="nsew")
        acciones = cabecera_tarjeta(
            tarjeta,
            "Inventario FTTH",
            "Precios en soles y disponibilidad en tiempo real",
        )
        self._pildora_conteo = Pildora(acciones, "0 productos", TEXTO_MEDIO, PANEL_ALT)
        self._pildora_conteo.pack(side="right")

        self.tabla = Tabla(
            tarjeta,
            [
                Columna("SKU", minimo=82),
                Columna("Producto", peso=3, minimo=210),
                Columna("Categoria", peso=1, minimo=135),
                Columna("Etiquetas", peso=1, minimo=130),
                Columna("Precio", minimo=95, anchor="e"),
                Columna("Stock", minimo=70, anchor="center"),
                Columna("Estado", minimo=78, anchor="center"),
            ],
            altura=380,
        )
        self.tabla.pack(fill="both", expand=True, padx=16, pady=(0, 4))

        self._pie = ctk.CTkLabel(
            tarjeta,
            text="",
            font=fuente(9),
            text_color=TEXTO_TENUE,
            anchor="w",
        )
        self._pie.pack(fill="x", padx=22, pady=(0, 14))

    def recargar(self) -> None:
        self._actualizar_filtro()
        self._render_tabla()

    def _actualizar_filtro(self) -> None:
        categorias = self.app.catalogo.listar_categorias()
        valores = ["Todas las categorias"] + [categoria.nombre for categoria in categorias]
        if self._filtro not in valores:
            self._filtro = "Todas las categorias"
        self.filtro.configure(values=valores)
        self.filtro.set(self._filtro)

    def _cambiar_filtro(self, valor: str) -> None:
        self._filtro = valor
        self._render_tabla()

    def _productos_filtrados(self):
        productos = self.app.catalogo.listar_productos()
        texto = self.busqueda.get().strip().lower()
        resultado = []
        for producto in productos:
            if self._filtro != "Todas las categorias" and producto.categoria.nombre != self._filtro:
                continue
            etiquetas = " ".join(etiqueta.nombre for etiqueta in producto.etiquetas)
            contenido = f"{producto.sku} {producto.nombre} {producto.categoria.nombre} {etiquetas}"
            if texto and texto not in contenido.lower():
                continue
            resultado.append(producto)
        return resultado

    def _render_tabla(self) -> None:
        productos = self._productos_filtrados()
        total = len(self.app.catalogo.listar_productos())
        self.tabla.limpiar()

        if not productos:
            self.tabla.vacio("No se encontraron productos con esos filtros.", icono="▤")
        for producto in productos:
            fila = self.tabla.fila()
            fila.celda(0, producto.sku, ACENTO, mono(10, True))
            fila.celda(1, truncar(producto.nombre, 34), TEXTO, fuente(11, True))
            fila.celda(2, truncar(producto.categoria.nombre, 20), TEXTO_SUAVE, fuente(10))
            etiquetas = " · ".join(etiqueta.nombre for etiqueta in producto.etiquetas[:3])
            if len(producto.etiquetas) > 3:
                etiquetas += f" +{len(producto.etiquetas) - 3}"
            fila.celda(3, etiquetas or "—", TEXTO_TENUE, fuente(9))
            fila.celda(4, formato_moneda(producto.precio), TEXTO_MEDIO, mono(10, True), anchor="e")

            stock = fila.contenedor(5)
            color, fondo = colores_stock(producto.stock)
            Pildora(stock, f"{producto.stock} und.", color, fondo).pack(anchor="center")

            estado = fila.contenedor(6)
            Pildora(estado, "Activo", ACENTO, "#0C2A27").pack(anchor="center")

        self._pildora_conteo.actualizar(
            f"{len(productos)} de {total} productos",
            TEXTO_MEDIO,
            PANEL_ALT,
        )
        valor = sum(producto.precio * producto.stock for producto in productos)
        self._pie.configure(
            text=(
                f"{len(productos)} referencias visibles · "
                f"valor del inventario filtrado: {formato_moneda(valor)}"
            )
        )

    def _abrir_producto(self) -> None:
        ModalProducto(self.app, self.app, self.recargar)

    def _abrir_categoria(self) -> None:
        ModalCategoria(self.app, self.app, self.recargar)


class ModalProducto(Modal):
    """Formulario de alta de un producto FTTH."""

    def __init__(self, maestro, app, al_guardar) -> None:
        super().__init__(
            maestro,
            "Nuevo producto",
            "Registra una referencia en el catalogo de OptiFiber",
            ancho=660,
            alto=610,
        )
        self.app = app
        self.al_guardar = al_guardar
        self.categorias = app.catalogo.listar_categorias()

        formulario = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        formulario.pack(fill="both", expand=True)
        formulario.grid_columnconfigure(0, weight=1)
        formulario.grid_columnconfigure(1, weight=1)

        self.sku = Campo(formulario, "SKU", "Ej. FIB-003")
        self.sku.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))

        self.nombre = Campo(formulario, "Nombre del producto", "Ej. Cable drop 2 hilos 150 m")
        self.nombre.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 12))

        self.precio = Campo(formulario, "Precio (S/)", "0.00")
        self.precio.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))

        self.stock = Campo(formulario, "Stock inicial", "0")
        self.stock.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 12))

        nombres = [categoria.nombre for categoria in self.categorias]
        self.categoria = Selector(formulario, "Categoria", nombres or ["Sin categorias"])
        self.categoria.grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))

        self.etiquetas = Campo(formulario, "Etiquetas", "hogar, empresa, promocion")
        self.etiquetas.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(0, 12))

        ctk.CTkLabel(
            formulario,
            text="Descripcion",
            font=fuente(10, True),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 5))

        self.descripcion = ctk.CTkTextbox(
            formulario,
            height=82,
            corner_radius=9,
            border_width=1,
            border_color=BORDE,
            fg_color=FONDO_ALT,
            text_color=TEXTO,
            font=fuente(11),
        )
        self.descripcion.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.agregar_boton("Cancelar", self.cerrar)
        self.agregar_boton("Guardar producto", self._guardar, "primario")
        self.sku.enfocar()

    def _guardar(self) -> None:
        self.limpiar_error()
        if not self.categorias:
            self.mostrar_error("Primero crea una categoria para poder registrar productos.")
            return

        try:
            precio = float(self.precio.valor().replace(",", "."))
            stock = int(self.stock.valor())
        except ValueError:
            self.mostrar_error("El precio y el stock deben ser numeros validos.")
            return

        etiquetas = [
            etiqueta.strip()
            for etiqueta in self.etiquetas.valor().split(",")
            if etiqueta.strip()
        ]
        categoria_id = next(
            categoria.id
            for categoria in self.categorias
            if categoria.nombre == self.categoria.valor()
        )

        try:
            producto = self.app.catalogo.crear_producto(
                sku=self.sku.valor(),
                nombre=self.nombre.valor(),
                precio=precio,
                stock=stock,
                categoria_id=categoria_id,
                descripcion=self.descripcion.get("1.0", "end").strip(),
                etiquetas=etiquetas,
            )
        except (ErrorDominio, ValueError) as exc:
            self.mostrar_error(str(exc))
            return

        self.al_guardar()
        self.cerrar()
        self.app.notificar(f"Producto {producto.sku} registrado correctamente.")


class ModalCategoria(Modal):
    """Formulario de alta de categorias comerciales."""

    def __init__(self, maestro, app, al_guardar) -> None:
        super().__init__(
            maestro,
            "Nueva categoria",
            "Agrupa los productos del catalogo",
            ancho=520,
            alto=390,
        )
        self.app = app
        self.al_guardar = al_guardar

        formulario = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        formulario.pack(fill="both", expand=True)

        self.nombre = Campo(formulario, "Nombre de la categoria", "Ej. Equipos ONT/ONU")
        self.nombre.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            formulario,
            text="Descripcion",
            font=fuente(10, True),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(anchor="w", pady=(0, 5))

        self.descripcion = ctk.CTkTextbox(
            formulario,
            height=90,
            corner_radius=9,
            border_width=1,
            border_color=BORDE,
            fg_color=FONDO_ALT,
            text_color=TEXTO,
            font=fuente(11),
        )
        self.descripcion.pack(fill="x")

        self.agregar_boton("Cancelar", self.cerrar)
        self.agregar_boton("Guardar categoria", self._guardar, "primario")
        self.nombre.enfocar()

    def _guardar(self) -> None:
        self.limpiar_error()
        try:
            categoria = self.app.catalogo.crear_categoria(
                self.nombre.valor(),
                self.descripcion.get("1.0", "end").strip(),
            )
        except (ErrorDominio, ValueError) as exc:
            self.mostrar_error(str(exc))
            return

        self.al_guardar()
        self.cerrar()
        self.app.notificar(f"Categoria {categoria.nombre} creada correctamente.")
