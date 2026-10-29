"""Pantalla de reportes comerciales y salud del inventario."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from src.presentacion.gui.componentes import (
    Columna,
    Pildora,
    Tabla,
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
    EXITO,
    EXITO_FONDO,
    INFO,
    INFO_FONDO,
    MORADO,
    MORADO_FONDO,
    PANEL,
    PANEL_ALT,
    PELIGRO,
    PELIGRO_FONDO,
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
    formato_moneda,
    truncar,
)

RAIZ_PROYECTO = Path(__file__).resolve().parents[4]
CARPETA_REPORTES = RAIZ_PROYECTO / "reportes"


class TarjetaReporte(ctk.CTkFrame):
    """Indicador compacto para la cabecera de reportes."""

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
        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=18, pady=(15, 0))

        chip = ctk.CTkFrame(cabecera, fg_color=fondo, width=25, height=25, corner_radius=8)
        chip.pack(side="left")
        chip.pack_propagate(False)
        ctk.CTkLabel(chip, text=icono, font=fuente(11, True), text_color=color).pack(expand=True)

        ctk.CTkLabel(
            cabecera,
            text=etiqueta.upper(),
            font=fuente(8, True),
            text_color=TEXTO_TENUE,
            anchor="w",
        ).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            self,
            text=valor,
            font=fuente(21, True),
            text_color=TEXTO,
            anchor="w",
        ).pack(fill="x", padx=18, pady=(5, 0))
        ctk.CTkLabel(
            self,
            text=pista,
            font=fuente(9),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(fill="x", padx=18, pady=(1, 14))


class PantallaReportes(ctk.CTkFrame):
    """Indicadores de ventas, productos mas vendidos y stock critico."""

    def __init__(self, maestro, app) -> None:
        super().__init__(maestro, fg_color="transparent", corner_radius=0)
        self.app = app
        self.pedidos = app.pedidos.listar()
        self.productos = app.catalogo.listar_productos()
        self.clientes = app.clientes.listar()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0, minsize=225)
        self.grid_rowconfigure(2, weight=1)

        self._construir_kpis()
        self._construir_ventas_y_stock()
        self._construir_productos_y_categorias()

    # ------------------------------------------------------------------
    # Cabecera
    # ------------------------------------------------------------------
    def _construir_kpis(self) -> None:
        activos = [pedido for pedido in self.pedidos if pedido.estado != "CANCELADO"]
        facturado = sum(pedido.total for pedido in activos)
        ticket = facturado / len(activos) if activos else 0.0
        descuentos = sum(
            max(0.0, sum(detalle.subtotal for detalle in pedido.detalles) - pedido.total)
            for pedido in activos
        )
        valor_inventario = sum(producto.precio * producto.stock for producto in self.productos)

        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        cabecera.grid_columnconfigure(0, weight=1)

        barra = ctk.CTkFrame(cabecera, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        barra.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            barra,
            text=(
                f"{len(self.pedidos)} pedidos · {len(self.clientes)} clientes · "
                f"{len(self.productos)} productos activos"
            ),
            font=fuente(10),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        boton_secundario(
            barra,
            "Exportar CSV",
            self._exportar,
            height=34,
            font=fuente(10, True),
        ).grid(row=0, column=1, padx=(0, 8))

        boton_primario(
            barra,
            "Ir a pedidos",
            lambda: self.app.ir_a("pedidos"),
            height=34,
            font=fuente(10, True),
        ).grid(row=0, column=2)

        kpis = ctk.CTkFrame(cabecera, fg_color="transparent")
        kpis.grid(row=1, column=0, sticky="ew")
        for indice in range(4):
            kpis.grid_columnconfigure(indice, weight=1)

        TarjetaReporte(
            kpis,
            "Facturacion",
            formato_moneda(facturado),
            f"{len(activos)} pedidos validos",
            ACENTO,
            ACENTO_FONDO,
            "↗",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))
        TarjetaReporte(
            kpis,
            "Ticket promedio",
            formato_moneda(ticket),
            "Por pedido no cancelado",
            INFO,
            INFO_FONDO,
            "◫",
        ).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        TarjetaReporte(
            kpis,
            "Descuentos",
            formato_moneda(descuentos),
            "Beneficio por volumen",
            MORADO,
            MORADO_FONDO,
            "%",
        ).grid(row=0, column=2, sticky="ew", padx=(0, 10))
        TarjetaReporte(
            kpis,
            "Inventario",
            formato_moneda(valor_inventario),
            f"{sum(producto.stock for producto in self.productos)} unidades",
            ALERTA,
            ALERTA_FONDO,
            "▤",
        ).grid(row=0, column=3, sticky="ew")

    # ------------------------------------------------------------------
    # Segunda fila: ventas por estado + stock critico
    # ------------------------------------------------------------------
    def _construir_ventas_y_stock(self) -> None:
        paneles = ctk.CTkFrame(self, fg_color="transparent")
        paneles.grid(row=1, column=0, sticky="nsew", pady=(0, 14))
        paneles.grid_rowconfigure(0, weight=1)
        paneles.grid_columnconfigure(0, weight=3)
        paneles.grid_columnconfigure(1, weight=2)

        self._tarjeta_ventas(paneles)
        self._tarjeta_stock(paneles)

    def _tarjeta_ventas(self, maestro) -> None:
        tarjeta = Tarjeta(maestro)
        tarjeta.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        resumen = self.app.pedidos.resumen_ventas()
        total = sum(float(datos["total"]) for datos in resumen.values()) or 1.0
        cabecera_tarjeta(
            tarjeta,
            "Ventas por estado",
            "Distribucion de la facturacion registrada",
            (
                formato_moneda(sum(float(d["total"]) for d in resumen.values())),
                TEXTO_MEDIO,
                PANEL_ALT,
            ),
        )

        cuerpo = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(2, 16))

        if not resumen:
            self._vacio(cuerpo, "Aun no hay pedidos para graficar.")
            return

        for indice, (estado, datos) in enumerate(resumen.items()):
            color, fondo = colores_estado(estado)
            cantidad = int(datos["cantidad"])
            monto = float(datos["total"])

            fila = ctk.CTkFrame(cuerpo, fg_color="transparent")
            fila.pack(fill="x", pady=(2 if indice else 0, 2))
            fila.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                fila,
                text=estado,
                font=fuente(9, True),
                text_color=color,
                anchor="w",
                height=18,
            ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                fila,
                text=f"{cantidad} pedidos · {formato_moneda(monto)}",
                font=mono(9),
                text_color=TEXTO_SUAVE,
                anchor="e",
                height=18,
            ).grid(row=0, column=1, sticky="e")

            barra = ctk.CTkProgressBar(
                fila,
                height=5,
                corner_radius=4,
                fg_color=fondo,
                progress_color=color,
                border_width=0,
            )
            barra.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 0))
            barra.set(max(0.03, monto / total))

    def _tarjeta_stock(self, maestro) -> None:
        tarjeta = Tarjeta(maestro)
        tarjeta.grid(row=0, column=1, sticky="nsew")
        criticos = [producto for producto in self.productos if producto.stock <= 5]
        acciones = cabecera_tarjeta(
            tarjeta,
            "Stock critico",
            "Cinco unidades o menos",
            (
                str(len(criticos)),
                PELIGRO if criticos else EXITO,
                PELIGRO_FONDO if criticos else EXITO_FONDO,
            ),
        )
        boton_secundario(
            acciones,
            "Catalogo",
            lambda: self.app.ir_a("catalogo"),
            height=28,
            font=fuente(9, True),
        ).pack(side="right")

        cuerpo = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(2, 16))

        if not criticos:
            self._vacio(cuerpo, "Todo el inventario esta saludable.", icono="✓")
            return

        for producto in criticos[:4]:
            fila = ctk.CTkFrame(cuerpo, fg_color=PANEL_ALT, corner_radius=10)
            fila.pack(fill="x", pady=3)
            fila.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                fila,
                text=truncar(producto.nombre, 28),
                font=fuente(10, True),
                text_color=TEXTO_MEDIO,
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=11, pady=(7, 0))
            ctk.CTkLabel(
                fila,
                text=f"{producto.sku} · {formato_moneda(producto.precio)}",
                font=mono(8),
                text_color=TEXTO_TENUE,
                anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=11, pady=(0, 7))

            color, fondo = colores_stock(producto.stock)
            Pildora(fila, f"{producto.stock} und.", color, fondo).grid(
                row=0,
                column=1,
                rowspan=2,
                padx=10,
            )

    # ------------------------------------------------------------------
    # Tercera fila: top productos + categorias
    # ------------------------------------------------------------------
    def _construir_productos_y_categorias(self) -> None:
        paneles = ctk.CTkFrame(self, fg_color="transparent")
        paneles.grid(row=2, column=0, sticky="nsew")
        paneles.grid_rowconfigure(0, weight=1)
        paneles.grid_columnconfigure(0, weight=3)
        paneles.grid_columnconfigure(1, weight=2)

        self._tarjeta_top(paneles)
        self._tarjeta_categorias(paneles)

    def _tarjeta_top(self, maestro) -> None:
        tarjeta = Tarjeta(maestro)
        tarjeta.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        cabecera_tarjeta(
            tarjeta,
            "Productos mas vendidos",
            "Ranking por unidades colocadas",
        )
        tabla = Tabla(
            tarjeta,
            [
                Columna("SKU", minimo=82),
                Columna("Producto", peso=3, minimo=200),
                Columna("Unidades", minimo=80, anchor="center"),
                Columna("Ingresos", minimo=105, anchor="e"),
            ],
            altura=160,
        )
        tabla.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        top = self.app.pedidos.productos_mas_vendidos(limite=4)
        if not top:
            tabla.vacio("Sin ventas registradas todavia.", icono="▦")
            return
        for fila_dato in top:
            fila = tabla.fila()
            fila.celda(0, str(fila_dato["sku"]), ACENTO, mono(9, True))
            fila.celda(1, truncar(str(fila_dato["nombre"]), 34), TEXTO_MEDIO, fuente(10))
            fila.celda(
                2,
                str(fila_dato["unidades"]),
                TEXTO,
                mono(10, True),
                anchor="center",
            )
            fila.celda(
                3,
                formato_moneda(float(fila_dato["ingresos"])),
                TEXTO,
                mono(9, True),
                anchor="e",
            )

    def _tarjeta_categorias(self, maestro) -> None:
        tarjeta = Tarjeta(maestro)
        tarjeta.grid(row=0, column=1, sticky="nsew")
        cabecera_tarjeta(
            tarjeta,
            "Inventario por categoria",
            "Unidades y valorizacion actual",
        )

        cuerpo = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(2, 16))

        categorias = self.app.catalogo.listar_categorias()
        filas = []
        for categoria in categorias:
            productos = [p for p in self.productos if p.categoria_id == categoria.id]
            if not productos:
                continue
            unidades = sum(producto.stock for producto in productos)
            valor = sum(producto.precio * producto.stock for producto in productos)
            filas.append((categoria.nombre, len(productos), unidades, valor))

        if not filas:
            self._vacio(cuerpo, "Sin productos registrados por categoria.")
            return

        maximo = max(unidades for _nombre, _cantidad, unidades, _valor in filas) or 1
        for nombre, cantidad, unidades, _valor in filas[:4]:
            fila = ctk.CTkFrame(cuerpo, fg_color="transparent")
            fila.pack(fill="x", pady=(3, 3))
            fila.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                fila,
                text=truncar(nombre, 28),
                font=fuente(9, True),
                text_color=TEXTO_MEDIO,
                anchor="w",
            ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                fila,
                text=f"{cantidad} ref. · {unidades} und.",
                font=mono(8),
                text_color=TEXTO_TENUE,
                anchor="e",
            ).grid(row=0, column=1, sticky="e")

            barra = ctk.CTkProgressBar(
                fila,
                height=6,
                corner_radius=4,
                fg_color=PANEL_ALT,
                progress_color=ACENTO,
                border_width=0,
            )
            barra.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))
            barra.set(max(0.04, unidades / maximo))

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _exportar(self) -> None:
        """Genera un CSV con el resumen comercial y el inventario."""
        CARPETA_REPORTES.mkdir(parents=True, exist_ok=True)
        marca = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = CARPETA_REPORTES / f"reporte_optifiber_{marca}.csv"

        activos = [pedido for pedido in self.pedidos if pedido.estado != "CANCELADO"]
        with ruta.open("w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            escritor.writerow(["REPORTE COMERCIAL OPTIFIBER"])
            escritor.writerow(["Generado", datetime.now().strftime("%d/%m/%Y %H:%M")])
            escritor.writerow([])
            escritor.writerow(["Pedidos", len(self.pedidos)])
            escritor.writerow(["Clientes", len(self.clientes)])
            escritor.writerow(["Productos", len(self.productos)])
            escritor.writerow(["Facturacion", f"{sum(p.total for p in activos):.2f}"])
            escritor.writerow([])
            escritor.writerow(["SKU", "Producto", "Categoria", "Precio", "Stock", "Valor"])
            for producto in self.productos:
                escritor.writerow(
                    [
                        producto.sku,
                        producto.nombre,
                        producto.categoria.nombre,
                        f"{producto.precio:.2f}",
                        producto.stock,
                        f"{producto.precio * producto.stock:.2f}",
                    ]
                )
            escritor.writerow([])
            escritor.writerow(["Pedido", "Fecha", "Cliente", "Documento", "Estado", "Total"])
            for pedido in self.pedidos:
                escritor.writerow(
                    [
                        f"#{pedido.id:03d}",
                        pedido.fecha.strftime("%d/%m/%Y"),
                        pedido.cliente.nombre,
                        pedido.cliente.documento,
                        pedido.estado,
                        f"{pedido.total:.2f}",
                    ]
                )

        self.app.notificar(f"Reporte exportado en {ruta.name}.", "exito")

    @staticmethod
    def _vacio(marco, mensaje: str, icono: str = "◌") -> None:
        ctk.CTkLabel(
            marco,
            text=icono,
            font=fuente(22),
            text_color=TEXTO_TENUE,
        ).pack(pady=(18, 2))
        ctk.CTkLabel(
            marco,
            text=mensaje,
            font=fuente(10),
            text_color=TEXTO_SUAVE,
        ).pack()
