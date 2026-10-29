# PBI-03 · Interfaz gráfica de escritorio

| Campo | Valor |
|---|---|
| **ID** | PBI-03 |
| **Empresa** | OPTIFIBER |
| **Producto** | Sistema de gestión comercial de productos FTTH |
| **Prioridad** | Alta |
| **Estimación** | 8 story points |
| **Sprint** | Sprint 5 · Experiencia de usuario |
| **Rama** | `feature/PBI-03-interfaz-grafica` |
| **Estado** | Terminado · fusionado a `main` |
| **Responsable** | Julio Cesar Diaz Tito (Frontend/UX/UI + QA) |
| **Apoyo técnico** | Omar Huallpayunca (Git Master), Kevin Llerena (backend), Amaru Ai-me (datos) |

---

## 1. Historia de usuario

**Como** asesor comercial de OPTIFIBER  
**deseo** gestionar clientes, productos, pedidos y reportes desde una aplicación de escritorio  
**para** operar el negocio sin depender de la terminal y presentar la información de forma clara.

### Contexto de negocio

La capa de persistencia del PBI-02 ya permite registrar clientes, productos y pedidos. Sin embargo, el uso diario en terminal resulta poco amigable para el personal comercial. El PBI-03 agrega una interfaz gráfica oscura, minimalista y funcional que reutiliza los repositorios y las reglas de negocio existentes.

---

## 2. Criterios de aceptación (Gherkin)

### Escenario 1 · Abrir la aplicación por defecto

```gherkin
Dado que el usuario ejecuta "python -m src.main"
Cuando la aplicación inicia
Entonces se abre la ventana de escritorio de OptiFiber
Y se muestra el panel general con indicadores y pedidos recientes
```

### Escenario 2 · Navegar entre pantallas

```gherkin
Dado que la ventana principal está abierta
Cuando el usuario selecciona una opción de la barra lateral
Entonces se muestra la pantalla correspondiente
Y la opción activa queda resaltada en turquesa
```

### Escenario 3 · Registrar un producto

```gherkin
Dado que el usuario está en la pantalla Catálogo
Cuando completa SKU, nombre, precio, stock y categoría
Y confirma el formulario
Entonces el producto se guarda en SQLite
Y la tabla del catálogo se actualiza sin reiniciar la aplicación
```

### Escenario 4 · Registrar un pedido

```gherkin
Dado un cliente seleccionado y productos con stock suficiente
Cuando el usuario agrega unidades al carrito y confirma el pedido
Entonces se crea el pedido con sus detalles
Y el stock se descuenta
Y se muestra el comprobante con el total y el descuento aplicable
```

### Escenario 5 · Eliminar un cliente con cascada

```gherkin
Dado un cliente con pedidos registrados
Cuando el usuario confirma la eliminación desde la ficha del cliente
Entonces se elimina el cliente, sus pedidos y sus detalles
Y la tabla de clientes se actualiza
```

### Escenario 6 · Exportar reportes

```gherkin
Dado que existen pedidos y productos registrados
Cuando el usuario pulsa "Exportar CSV" en Reportes
Entonces se genera un archivo CSV en la carpeta "reportes/"
Y se muestra un aviso de confirmación
```

### Escenario 7 · Mantener la terminal disponible

```gherkin
Dado que se requiere una demostración o automatización
Cuando el usuario ejecuta "python -m src.main --cli" o "--demo"
Entonces se ejecuta la interfaz de terminal existente
```

---

## 3. Criterios de aceptación técnicos

- [x] GUI funcional con CustomTkinter, sin dependencia obligatoria de la terminal.
- [x] Tema oscuro con texto claro y acento turquesa; sin imágenes pesadas.
- [x] Cinco pantallas: panel general, catálogo, clientes, pedidos y reportes.
- [x] Navegación lateral, barra superior contextual y atajos `Ctrl+1` … `Ctrl+5`.
- [x] Formularios modales para producto, categoría, cliente y detalle de pedido.
- [x] Punto de venta con carrito, validación de stock y cálculo de totales.
- [x] Eliminación de clientes con confirmación y cascada del ORM.
- [x] Reportes con KPIs, ventas por estado, top de productos y stock crítico.
- [x] Exportación de reportes a CSV.
- [x] Pedidos demo idempotentes para el primer arranque.
- [x] Icono de aplicación en `assets/optifiber.ico`.
- [x] 23 pruebas en verde y Ruff sin errores.
- [x] Capturas de las pantallas en `docs/evidencias/gui/`.

---

## 4. Definition of Done

1. El código está en la rama `feature/PBI-03-interfaz-grafica`.
2. `python -m src.main` abre la interfaz gráfica sin errores.
3. `python -m src.main --cli` y `--demo` siguen funcionando.
4. `python -m pytest -q` reporta 23 pruebas aprobadas.
5. `python -m ruff check .` reporta `All checks passed!`.
6. La aplicación permite crear clientes, productos, pedidos y actualizar estados.
7. Las capturas de las cinco pantallas están en `docs/evidencias/gui/`.
8. El README y el Capítulo 4 documentan la interfaz.
9. El PR fue revisado y fusionado a `main`.
10. Se creó el tag `pbi-03-gui-v1.0`.

---

## 5. Evidencias

| Evidencia | Ubicación |
|---|---|
| Historia y criterios | Este documento |
| Ventana principal | `src/presentacion/gui/app.py` |
| Componentes visuales | `src/presentacion/gui/componentes.py` |
| Paleta y tipografías | `src/presentacion/gui/tema.py` |
| Pantallas | `src/presentacion/gui/pantallas/` |
| Icono | `assets/optifiber.ico` |
| Capturas | `docs/evidencias/gui/01_panel_general.png` … `08_modal_cliente.png` |
| Pruebas | `tests/test_seed.py` y suite completa |
| Informe | `docs/INFORME_CAPITULO_4.md` y `.docx` |
