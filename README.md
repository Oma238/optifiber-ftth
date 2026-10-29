# OptiFiber FTTH · PBI-02 + PBI-03

Sistema de gestión comercial para **OPTIFIBER**, empresa dedicada a la venta de productos FTTH (fibra óptica, equipos ONT/ONU, accesorios, herramientas y conectividad). El proyecto implementa la capa de persistencia con **SQLAlchemy 2.x**, relaciones **1:N y N:M**, **eliminación en cascada**, pruebas con **pytest** sobre **SQLite en memoria**, un pipeline de **GitHub Actions** y una **aplicación de escritorio** con interfaz gráfica oscura construida con **CustomTkinter**.

> **Curso:** Construcción de Software  
> **Trabajo:** Instructivo de Trabajo Colaborativo N° 04 · Persistencia de Datos, Mapeo ORM y Pruebas con Fixtures  
> **Empresa:** OPTIFIBER  
> **PBI:** PBI-02 · Persistencia de clientes, pedidos y catálogo FTTH + PBI-03 · Interfaz gráfica de escritorio

---

## 1. Integrantes y roles

| Integrante | Rol principal | GitHub sugerido | Responsabilidad |
|---|---|---|---|
| **Huallpayunca Carrion Omar Sebastian** | Git Master + Product Owner / Scrum Master | `@omarhuallpayunca` | Repositorio, ramas `feature/PBI-02-orm-persistencia` y `feature/PBI-03-interfaz-grafica`, PBI, revisión de PR, merges y coordinación del informe. |
| **Kevin Jesus Llerena Fernandez** | Lead Backend Engineer | `@kevinllerena` | Reglas de negocio puras en `src/dominio`, servicios de totales/descuento/stock y capa de repositorios. |
| **Amaru Josue Ai-me Yunguri** | Database & ORM Specialist | `@amaruaime` | ERD, modelos ORM, claves foráneas, relaciones 1:N y N:M, reglas de cascada y restricciones. |
| **Julio Cesar Diaz Tito** | DevOps & QA Engineer + Frontend/UX/UI Engineer | `@juliodiaz` | Fixture `db_session`, suite pytest, Ruff, GitHub Actions, pantallas CustomTkinter, tema oscuro y evidencias del informe. |

> El instructivo propone 5 roles. El equipo tiene 4 integrantes, por lo que se combinaron así: **Omar** asume Git Master + PO/SM y **Julio** asume DevOps/QA + Frontend/UX. El detalle está en [`docs/DISTRIBUCION_EQUIPO.md`](docs/DISTRIBUCION_EQUIPO.md).

---

## 2. Funcionalidades

- **Catálogo FTTH:** categorías, productos, SKU único, precios, stock, etiquetas y alerta de stock bajo.
- **Clientes:** DNI/RUC validado, datos de contacto, unicidad de documento e historial de pedidos.
- **Pedidos:** registro con múltiples líneas, cálculo de subtotales, descuento por volumen del 5 % desde S/ 1 500 y descuento automático de stock.
- **Relación 1:N:** `Cliente 1:N Pedido` y `Pedido 1:N DetallePedido`.
- **Relación N:M:** `Producto N:M Etiqueta` mediante `producto_etiqueta`; además, `DetallePedido` resuelve la N:M entre pedido y producto con datos adicionales (cantidad, precio, subtotal).
- **Cascada:** al eliminar un cliente se eliminan sus pedidos y los detalles de esos pedidos (`cascade="all, delete-orphan"`).
- **Aplicación de escritorio:** cinco pantallas funcionales (panel general, catálogo, clientes, pedidos y reportes) con CustomTkinter, tema oscuro, navegación lateral y formularios modales.
- **Reportes:** KPIs de facturación y ticket promedio, ventas por estado, productos más vendidos, stock crítico, inventario por categoría y exportación a CSV.
- **CLI opcional:** catálogo, alta de clientes, pedidos, historial, reporte de ventas, stock bajo y demostración de cascada mediante `--cli`.
- **Calidad:** 23 pruebas automatizadas, Ruff sin errores y workflow de CI.

---

## 3. ERD

![Modelo Entidad-Relación de OptiFiber](docs/erd_optifiber.png)

Fuente editable: [`docs/erd_optifiber.mmd`](docs/erd_optifiber.mmd) (Mermaid) y script de generación: [`scripts/generar_erd.py`](scripts/generar_erd.py).

```mermaid
erDiagram
    CLIENTE ||--o{ PEDIDO : realiza
    PEDIDO ||--|{ DETALLE_PEDIDO : contiene
    PRODUCTO ||--o{ DETALLE_PEDIDO : referencia
    CATEGORIA ||--o{ PRODUCTO : clasifica
    PRODUCTO }o--o{ ETIQUETA : etiquetado
```

---

## 4. Arquitectura

```text
optifiber-ftth/
├── .github/workflows/ci.yml       # Ruff + pytest en GitHub Actions
├── assets/
│   └── optifiber.ico              # Icono de la aplicación
├── src/
│   ├── dominio/                   # Reglas puras: totales, descuento, stock, documento
│   │   └── servicios.py
│   ├── infraestructura/           # Persistencia SQLAlchemy
│   │   ├── modelos.py             # Base + 6 entidades ORM
│   │   ├── db.py                  # Engine, sesión y PRAGMA foreign_keys
│   │   ├── repositorios.py        # Clientes, catálogo y pedidos
│   │   └── seed.py                # Datos demo y pedidos iniciales
│   ├── presentacion/
│   │   ├── cli.py                 # Interfaz de consola (modo alternativo)
│   │   └── gui/
│   │       ├── app.py             # Ventana principal, navegación y sesión
│   │       ├── tema.py            # Paleta oscura, tipografías y radios
│   │       ├── componentes.py     # Tarjetas, tablas, modales y avisos
│   │       ├── utilidades.py      # Formatos y colores semánticos
│   │       └── pantallas/         # Panel, catálogo, clientes, pedidos, reportes
│   └── main.py                    # Punto de entrada (GUI por defecto)
├── tests/
│   ├── conftest.py                # Fixture db_session (sqlite:///:memory:)
│   ├── test_persistencia_orm.py   # 1:N, cascada, N:M, UNIQUE
│   ├── test_dominio.py            # Reglas de negocio
│   ├── test_repositorios.py       # Integración de repositorios
│   └── test_seed.py               # Datos demo idempotentes
├── docs/                          # Informe, PBI, roles, ERD y evidencias
├── scripts/                       # Generación del ERD, icono e informe DOCX
├── requirements.txt
└── pyproject.toml
```

La dirección de dependencias es `presentacion → infraestructura → dominio`; `src/dominio` no importa SQLAlchemy ni conoce la base de datos. La GUI reutiliza los repositorios existentes y no duplica reglas de negocio.

---

## 5. Interfaz gráfica de escritorio

La aplicación abre por defecto con `python -m src.main`. Usa **CustomTkinter** con una paleta oscura (`#070B10`), texto claro y acentos turquesa. La navegación lateral permite cambiar de pantalla con el mouse o con `Ctrl+1` … `Ctrl+5`; `F5` refresca la vista actual.

| Pantalla | Qué permite hacer |
|---|---|
| **Panel general** | Ver ingresos, pedidos, clientes, productos, pedidos recientes y stock bajo. |
| **Catálogo** | Buscar y filtrar productos, crear categorías y registrar nuevos productos con etiquetas. |
| **Clientes** | Buscar clientes, consultar su ficha e historial, crear clientes y eliminarlos con cascada. |
| **Pedidos** | Armar un pedido con carrito, validar stock, confirmar la venta y cambiar el estado del pedido. |
| **Reportes** | Consultar KPIs, ventas por estado, productos más vendidos, stock crítico y exportar un CSV. |

![Panel general de OptiFiber](docs/evidencias/gui/01_panel_general.png)

**Figura G1.** Panel general con indicadores, pedidos recientes y alertas de stock.

![Catálogo de productos FTTH](docs/evidencias/gui/02_catalogo.png)

**Figura G2.** Catálogo con búsqueda, filtro por categoría y alta de productos.

![Punto de venta de pedidos](docs/evidencias/gui/04_pedidos.png)

**Figura G3.** Punto de venta: cliente, productos, carrito y confirmación del pedido.

![Reportes comerciales](docs/evidencias/gui/05_reportes.png)

**Figura G4.** Reportes comerciales, ranking de productos y salud del inventario.

Los formularios y fichas se abren en ventanas modales oscuras; por ejemplo, el detalle de un pedido permite actualizar su estado sin salir de la pantalla.

![Detalle de pedido](docs/evidencias/gui/07_modal_pedido.png)

**Figura G5.** Detalle del pedido con líneas, totales y cambio de estado.

La interfaz mantiene la terminal disponible para demostraciones y automatización: `python -m src.main --cli` y `python -m src.main --demo`.

---

## 6. Puesta en marcha

Requisitos: **Python 3.12+** (probado con 3.14.6) y Git.

```powershell
cd optifiber-ftth
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Aplicación de escritorio (recomendado)

```powershell
python -m src.main
```

Abre la interfaz gráfica con la base persistente `data/optifiber.db`. En el primer arranque se cargan el catálogo, los clientes y pedidos de demostración para que el panel tenga actividad.

### Menú interactivo en la terminal (modo alternativo)

```powershell
python -m src.main --cli
```

Opciones: catálogo, registrar cliente, listar clientes, registrar pedido, listar pedidos, reporte de ventas/stock y eliminar cliente con cascada.

### Demostración automática (SQLite en memoria)

```powershell
python -m src.main --demo
```

Genera el catálogo, clientes, un pedido corporativo con descuento y evidencia la eliminación en cascada.

### Base de datos personalizada

```powershell
python -m src.main --db "sqlite:///data/mi_base.db"
python -m src.main --cli --db "sqlite:///data/mi_base.db"
```

---

## 7. Pruebas y calidad

```powershell
python -m pytest -v
python -m ruff check .
```

Resultado actual:

```text
23 passed in 0.19s
All checks passed!
```

Evidencias: [`docs/evidencias/pytest_final.txt`](docs/evidencias/pytest_final.txt), [`docs/evidencias/ruff_final.txt`](docs/evidencias/ruff_final.txt), [`docs/evidencias/demo_final.txt`](docs/evidencias/demo_final.txt) y las capturas en [`docs/evidencias/gui/`](docs/evidencias/gui/).

### Cobertura de pruebas

| Archivo | Pruebas | Qué verifica |
|---|---:|---|
| `tests/test_persistencia_orm.py` | 5 | Cliente–Pedido 1:N, cascada, N:M Producto–Etiqueta, cascada Pedido–Detalle, documento único. |
| `tests/test_dominio.py` | 10 | Subtotal, descuento por volumen, stock, cantidades y DNI/RUC. |
| `tests/test_repositorios.py` | 6 | Alta de pedidos, descuento de stock, descuento, stock insuficiente, documento duplicado y cascada. |
| `tests/test_seed.py` | 2 | Carga inicial del catálogo y pedidos demo idempotentes. |
| **Total** | **23** | Suite hermética sobre `sqlite:///:memory:`. |

---

## 8. Historial TDD

| Etapa | Commit | Autor |
|---|---|---|
| Estructura inicial | `cc4e5e7` | Omar Huallpayunca |
| Fixture + clase Base | `c394468` | Julio Diaz |
| RED ciclo 1 | `b292e8c` | Julio Diaz |
| GREEN ciclo 1 | `c368e49` | Amaru Ai-me |
| RED ciclo 2 | `33febea` | Julio Diaz |
| GREEN ciclo 2 | `72e423d` | Amaru Ai-me |
| RED ciclo 3 | `e397f22` | Julio Diaz |
| GREEN ciclo 3 | `df33bcd` | Amaru Ai-me |
| RED dominio | `0bf652a` | Kevin Llerena |
| GREEN dominio | `4f6d01c` | Kevin Llerena |
| RED repositorios | `417ed0f` | Julio Diaz |
| GREEN repositorios | `27071a2` | Kevin Llerena |
| REFACTOR | `9268085` | Julio Diaz |
| Interfaz GUI (PBI-03) | `37b0a15` | Julio Diaz |
| Pruebas de datos demo | `f2bf169` | Julio Diaz |

El detalle completo está en [`docs/evidencias/commits.md`](docs/evidencias/commits.md).

---

## 9. Documentación

- [`docs/INFORME_CAPITULO_4.md`](docs/INFORME_CAPITULO_4.md) — Capítulo 4 completo (4.1 ERD, 4.2 ORM, 4.3 fixture/TDD, 4.4 interfaz gráfica).
- [`docs/Informe_Capitulo_4_OptiFiber.docx`](docs/Informe_Capitulo_4_OptiFiber.docx) — versión Word para entrega.
- [`docs/PBI-02.md`](docs/PBI-02.md) — historia de usuario, criterios Gherkin y DoD de persistencia.
- [`docs/PBI-03.md`](docs/PBI-03.md) — historia de usuario, criterios Gherkin y DoD de la interfaz gráfica.
- [`docs/DISTRIBUCION_EQUIPO.md`](docs/DISTRIBUCION_EQUIPO.md) — reparto de funciones y aportes por integrante.
- [`docs/GUIA_GIT_Y_ENTREGA.md`](docs/GUIA_GIT_Y_ENTREGA.md) — publicación en GitHub, PR, CI y checklist.
- [`docs/MATRIZ_EVALUACION.md`](docs/MATRIZ_EVALUACION.md) — checklist del docente con evidencias.

---

## 10. Estado del PBI

**PBI-02:** implementado, probado y aprobado. Rama `feature/PBI-02-orm-persistencia` fusionada a `main` mediante el merge **`329b4ea`** (PR #2) y tag **`pbi-02-v1.0`**. Pipeline esperado: `ruff check .` y `pytest -v` en verde.

**PBI-03:** implementado y probado en la rama `feature/PBI-03-interfaz-grafica` (commits `37b0a15` y `f2bf169`). La aplicación de escritorio abre con `python -m src.main`, cubre las cinco pantallas y mantiene la CLI. Suite final: **23 passed**; Ruff: **All checks passed!** El merge a `main` y el tag **`pbi-03-gui-v1.0`** se registran al cierre de la entrega.
