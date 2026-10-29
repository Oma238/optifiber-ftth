"""Pantalla de clientes y su historial de compras."""

from __future__ import annotations

import customtkinter as ctk

from src.dominio.servicios import ErrorDominio
from src.presentacion.gui.componentes import (
    Campo,
    Columna,
    Modal,
    ModalConfirmacion,
    Pildora,
    Tabla,
    Tarjeta,
    boton_peligro,
    boton_primario,
    boton_secundario,
    cabecera_tarjeta,
)
from src.presentacion.gui.tema import (
    ACENTO,
    ACENTO_FONDO,
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
    colores_estado,
    formato_fecha,
    formato_moneda,
    iniciales,
    truncar,
)


class PantallaClientes(ctk.CTkFrame):
    """Directorio de clientes con acceso a su historial y eliminacion en cascada."""

    def __init__(self, maestro, app) -> None:
        super().__init__(maestro, fg_color="transparent", corner_radius=0)
        self.app = app
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
            placeholder_text="Buscar por nombre, documento o correo...",
            placeholder_text_color=TEXTO_TENUE,
            height=38,
            width=400,
            corner_radius=10,
            border_width=1,
            fg_color=FONDO_ALT,
            border_color=BORDE,
            text_color=TEXTO,
            font=fuente(11),
        )
        self.busqueda.grid(row=0, column=0, sticky="w")
        self.busqueda.bind("<KeyRelease>", lambda _evento: self._render_tabla())

        boton_primario(
            barra,
            "+  Nuevo cliente",
            self._abrir_cliente,
            height=38,
            font=fuente(11, True),
        ).grid(row=0, column=1)

    def _construir_tarjeta(self) -> None:
        tarjeta = Tarjeta(self)
        tarjeta.grid(row=1, column=0, sticky="nsew")
        acciones = cabecera_tarjeta(
            tarjeta,
            "Directorio de clientes",
            "Personas naturales y empresas registradas",
        )
        self._pildora_conteo = Pildora(acciones, "0 clientes", TEXTO_MEDIO, PANEL_ALT)
        self._pildora_conteo.pack(side="right")

        self.tabla = Tabla(
            tarjeta,
            [
                Columna("Documento", minimo=105),
                Columna("Cliente", peso=3, minimo=200),
                Columna("Telefono", minimo=105),
                Columna("Correo", peso=2, minimo=180),
                Columna("Pedidos", minimo=70, anchor="center"),
                Columna("", minimo=60, anchor="center"),
            ],
            altura=400,
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
        self._render_tabla()

    def _clientes_filtrados(self):
        clientes = self.app.clientes.listar()
        texto = self.busqueda.get().strip().lower()
        resultado = []
        for cliente in clientes:
            contenido = f"{cliente.nombre} {cliente.documento} {cliente.email} {cliente.telefono}"
            if texto and texto not in contenido.lower():
                continue
            resultado.append(cliente)
        return resultado

    def _render_tabla(self) -> None:
        clientes = self._clientes_filtrados()
        total = len(self.app.clientes.listar())
        self.tabla.limpiar()

        if not clientes:
            self.tabla.vacio("No se encontraron clientes con esa busqueda.", icono="◍")

        for cliente in clientes:
            fila = self.tabla.fila()
            fila.celda(0, cliente.documento, TEXTO_SUAVE, mono(10, True))
            fila.celda(1, truncar(cliente.nombre, 32), TEXTO, fuente(11, True))
            fila.celda(2, cliente.telefono or "—", TEXTO_SUAVE, fuente(10))
            fila.celda(3, truncar(cliente.email or "—", 26), TEXTO_TENUE, fuente(9))
            fila.celda(
                4,
                str(len(cliente.pedidos)),
                TEXTO_MEDIO,
                mono(10, True),
                anchor="center",
            )

            contenedor = fila.contenedor(5)
            boton_secundario(
                contenedor,
                "Ver",
                lambda c=cliente: self._abrir_detalle(c),
                width=52,
                height=27,
                font=fuente(9, True),
            ).pack(anchor="center")

        facturado = sum(
            pedido.total for cliente in clientes for pedido in cliente.pedidos
        )
        self._pildora_conteo.actualizar(
            f"{len(clientes)} de {total} clientes",
            TEXTO_MEDIO,
            PANEL_ALT,
        )
        self._pie.configure(
            text=(
                f"{len(clientes)} clientes visibles · "
                f"facturacion acumulada: {formato_moneda(facturado)}"
            )
        )

    def _abrir_cliente(self) -> None:
        ModalClienteNuevo(self.app, self.app, self.recargar)

    def _abrir_detalle(self, cliente) -> None:
        ModalCliente(self.app, self.app, cliente, self.recargar)


class ModalClienteNuevo(Modal):
    """Formulario de alta de clientes con validacion de DNI o RUC."""

    def __init__(self, maestro, app, al_guardar) -> None:
        super().__init__(
            maestro,
            "Nuevo cliente",
            "Registra los datos de contacto del comprador",
            ancho=600,
            alto=600,
        )
        self.app = app
        self.al_guardar = al_guardar

        formulario = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        formulario.pack(fill="both", expand=True)
        formulario.grid_columnconfigure(0, weight=1)
        formulario.grid_columnconfigure(1, weight=1)

        self.nombre = Campo(formulario, "Nombre o razon social", "Ej. Ana Quispe")
        self.nombre.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        self.documento = Campo(formulario, "Documento", "DNI 8 digitos o RUC 11 digitos")
        self.documento.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))

        self.telefono = Campo(formulario, "Telefono", "Ej. 987654321")
        self.telefono.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 12))

        self.email = Campo(formulario, "Correo electronico", "cliente@correo.com")
        self.email.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        self.direccion = Campo(formulario, "Direccion", "Av. Los Alamos 123, Lima")
        self.direccion.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.agregar_boton("Cancelar", self.cerrar)
        self.agregar_boton("Guardar cliente", self._guardar, "primario")
        self.nombre.enfocar()

    def _guardar(self) -> None:
        self.limpiar_error()
        try:
            cliente = self.app.clientes.crear(
                nombre=self.nombre.valor(),
                documento=self.documento.valor(),
                telefono=self.telefono.valor(),
                email=self.email.valor(),
                direccion=self.direccion.valor(),
            )
        except (ErrorDominio, ValueError) as exc:
            self.mostrar_error(str(exc))
            return

        self.al_guardar()
        self.cerrar()
        self.app.notificar(f"Cliente {cliente.nombre} registrado correctamente.")


class ModalCliente(Modal):
    """Ficha completa del cliente con historial y acciones."""

    def __init__(self, maestro, app, cliente, al_actualizar) -> None:
        super().__init__(
            maestro,
            f"Cliente · {cliente.nombre}",
            "Ficha comercial e historial de pedidos",
            ancho=640,
            alto=680,
            scrollable=True,
        )
        self.app = app
        self.cliente = cliente
        self.al_actualizar = al_actualizar

        hero = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        hero.pack(fill="x", pady=(0, 16))

        avatar = ctk.CTkFrame(
            hero,
            fg_color=ACENTO_FONDO,
            width=52,
            height=52,
            corner_radius=15,
        )
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(
            avatar,
            text=iniciales(cliente.nombre),
            font=fuente(18, True),
            text_color=ACENTO,
        ).pack(expand=True)

        identidad = ctk.CTkFrame(hero, fg_color="transparent")
        identidad.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(
            identidad,
            text=cliente.nombre,
            font=fuente(16, True),
            text_color=TEXTO,
            anchor="w",
        ).pack(anchor="w")
        tipo = "RUC" if len(cliente.documento) == 11 else "DNI"
        ctk.CTkLabel(
            identidad,
            text=f"{tipo} · {cliente.documento}",
            font=mono(10),
            text_color=TEXTO_SUAVE,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        Pildora(
            hero,
            "Cliente activo",
            ACENTO,
            ACENTO_FONDO,
        ).pack(side="right")

        contacto = ctk.CTkFrame(self.cuerpo, fg_color=PANEL_ALT, corner_radius=12)
        contacto.pack(fill="x", pady=(0, 14))
        datos = [
            ("Telefono", cliente.telefono or "No registrado"),
            ("Correo", cliente.email or "No registrado"),
            ("Direccion", cliente.direccion or "No registrada"),
            ("Registrado", formato_fecha(cliente.creado_en.date())),
        ]
        for indice, (etiqueta, valor) in enumerate(datos):
            relleno = (10 if indice == 0 else 3, 10 if indice == 3 else 3)
            ctk.CTkLabel(
                contacto,
                text=etiqueta,
                font=fuente(9, True),
                text_color=TEXTO_TENUE,
                anchor="w",
                width=82,
            ).grid(
                row=indice,
                column=0,
                sticky="w",
                padx=(14, 8),
                pady=relleno,
            )
            ctk.CTkLabel(
                contacto,
                text=truncar(valor, 48),
                font=fuente(10),
                text_color=TEXTO_MEDIO,
                anchor="w",
            ).grid(
                row=indice,
                column=1,
                sticky="w",
                padx=(0, 14),
                pady=relleno,
            )

        metricas = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        metricas.pack(fill="x", pady=(0, 16))
        metricas.grid_columnconfigure(0, weight=1)
        metricas.grid_columnconfigure(1, weight=1)

        self._metrica(metricas, 0, "Pedidos realizados", str(len(cliente.pedidos)))
        total = sum(pedido.total for pedido in cliente.pedidos)
        self._metrica(metricas, 1, "Total comprado", formato_moneda(total))

        ctk.CTkLabel(
            self.cuerpo,
            text="HISTORIAL DE PEDIDOS",
            font=fuente(9, True),
            text_color=TEXTO_TENUE,
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        if not cliente.pedidos:
            marco = ctk.CTkFrame(self.cuerpo, fg_color=PANEL_ALT, corner_radius=12)
            marco.pack(fill="x")
            ctk.CTkLabel(
                marco,
                text="Este cliente aun no tiene pedidos registrados.",
                font=fuente(10),
                text_color=TEXTO_SUAVE,
            ).pack(pady=20)
        else:
            for pedido in cliente.pedidos[-6:]:
                fila = ctk.CTkFrame(self.cuerpo, fg_color=PANEL_ALT, corner_radius=11)
                fila.pack(fill="x", pady=3)
                fila.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(
                    fila,
                    text=f"#{pedido.id:03d} · {formato_fecha(pedido.fecha)}",
                    font=fuente(10, True),
                    text_color=TEXTO_MEDIO,
                    anchor="w",
                ).grid(row=0, column=0, sticky="w", padx=12, pady=10)
                color, fondo = colores_estado(pedido.estado)
                Pildora(fila, pedido.estado, color, fondo).grid(row=0, column=1, padx=8)
                ctk.CTkLabel(
                    fila,
                    text=formato_moneda(pedido.total),
                    font=mono(10, True),
                    text_color=TEXTO,
                    anchor="e",
                ).grid(row=0, column=2, sticky="e", padx=(0, 12))

        boton_peligro(
            self._acciones,
            "Eliminar cliente",
            self._confirmar_eliminar,
            height=36,
            font=fuente(10, True),
        ).pack(side="left")

        self.agregar_boton("Cerrar", self.cerrar)
        self.agregar_boton("Nuevo pedido", self._nuevo_pedido, "primario")

    @staticmethod
    def _metrica(maestro, columna: int, etiqueta: str, valor: str) -> None:
        tarjeta = ctk.CTkFrame(
            maestro,
            fg_color=PANEL_ALT,
            corner_radius=12,
        )
        tarjeta.grid(
            row=0,
            column=columna,
            sticky="ew",
            padx=(0, 6) if columna == 0 else (6, 0),
        )
        ctk.CTkLabel(
            tarjeta,
            text=etiqueta.upper(),
            font=fuente(8, True),
            text_color=TEXTO_TENUE,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(11, 0))
        ctk.CTkLabel(
            tarjeta,
            text=valor,
            font=fuente(16, True),
            text_color=TEXTO,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(1, 11))

    def _nuevo_pedido(self) -> None:
        documento = self.cliente.documento
        self.cerrar()
        self.app.ir_a("pedidos", cliente_documento=documento)

    def _confirmar_eliminar(self) -> None:
        cantidad = len(self.cliente.pedidos)
        ModalConfirmacion(
            self,
            "Eliminar cliente",
            (
                f"Se eliminara a {self.cliente.nombre} y sus {cantidad} pedido(s). "
                "La operacion aplica la cascada configurada en el ORM y no se puede deshacer."
            ),
            "Eliminar de todas formas",
            self._eliminar,
        )

    def _eliminar(self) -> None:
        nombre = self.cliente.nombre
        self.app.clientes.eliminar(self.cliente.id)
        self.al_actualizar()
        self.cerrar()
        self.app.notificar(f"{nombre} y sus pedidos fueron eliminados en cascada.", "alerta")
