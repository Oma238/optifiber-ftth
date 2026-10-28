# PBI-02 · Persistencia de clientes, pedidos y catálogo FTTH

| Campo | Valor |
|---|---|
| **ID** | PBI-02 |
| **Empresa** | OPTIFIBER |
| **Producto** | Sistema de gestión comercial de productos FTTH |
| **Prioridad** | Alta |
| **Estimación** | 8 story points |
| **Sprint** | Sprint 4 · Persistencia y calidad |
| **Rama** | `feature/PBI-02-orm-persistencia` |
| **Estado** | Terminado · fusionado a `main` |
| **Responsable** | Huallpayunca Carrion Omar Sebastian (Git Master + PO/SM) |
| **Apoyo técnico** | Amaru Ai-me (ORM), Kevin Llerena (backend), Julio Diaz (QA/DevOps) |

---

## 1. Historia de usuario

**Como** asesor comercial de OPTIFIBER  
**deseo** registrar clientes, productos y pedidos con sus líneas de detalle  
**para** consultar el historial de compras, controlar el stock y calcular el total con descuentos.

### Contexto de negocio

OPTIFIBER vende productos FTTH: cable drop, cable ADSS, ONT/ONU, rosetas, conectores, fusionadoras, OTDR, switches y routers. El asesor necesita identificar al cliente por DNI o RUC, armar un pedido con varios productos, validar stock y conservar el historial aunque se elimine un cliente (en cuyo caso la cascada elimina sus pedidos por política de privacidad).

---

## 2. Criterios de aceptación (Gherkin)

### Escenario 1 · Guardar un cliente con sus pedidos (1:N)

```gherkin
Dado un cliente "Ana Quispe" con documento "12345678"
Cuando se registran dos pedidos asociados al cliente
Y se persiste el cliente en la base de datos
Entonces se consulta el cliente por nombre
Y se recuperan sus dos pedidos con la relación inversa al cliente
```

**Prueba:** `tests/test_persistencia_orm.py::test_guardar_cliente_con_sus_pedidos`  
**Commits:** `b292e8c` (RED) → `c368e49` (GREEN)

### Escenario 2 · Eliminar un cliente elimina sus pedidos (cascada)

```gherkin
Dado un cliente con un pedido persistido
Cuando se elimina el cliente
Entonces sus pedidos también desaparecen de la base de datos
Y no queda ningún registro huérfano
```

**Prueba:** `tests/test_persistencia_orm.py::test_eliminar_cliente_elimina_sus_pedidos`  
**Commits:** `33febea` (RED) → `72e423d` (GREEN)

### Escenario 3 · Consultar un producto con sus etiquetas (N:M)

```gherkin
Dado un producto "ONT-001" con las etiquetas "hogar" y "empresa"
Cuando se persiste el producto
Y se consulta por su SKU
Entonces se recuperan sus dos etiquetas
Y desde cada etiqueta se puede navegar de vuelta al producto
```

**Prueba:** `tests/test_persistencia_orm.py::test_relacion_nm_producto_etiqueta`  
**Commits:** `e397f22` (RED) → `df33bcd` (GREEN)

### Escenario 4 · Registrar un pedido con detalle, stock y descuento

```gherkin
Dado un cliente y un producto con stock suficiente
Cuando se registra un pedido con dos unidades
Entonces se crea una línea de detalle con cantidad, precio unitario y subtotal
Y el stock del producto disminuye en dos unidades
Y el total del pedido se calcula según las reglas de dominio
```

**Pruebas:** `tests/test_repositorios.py::test_crear_pedido_descuenta_stock_y_calcula_total` y `test_crear_pedido_aplica_descuento_por_volumen`  
**Commits:** `417ed0f` (RED) → `27071a2` (GREEN)

### Escenario 5 · Rechazar un pedido sin stock

```gherkin
Dado un producto con stock 10
Cuando se intenta registrar un pedido por 99 unidades
Entonces la operación se rechaza con un error de dominio
Y el stock permanece sin cambios
Y no se guarda ningún detalle de pedido
```

**Prueba:** `tests/test_repositorios.py::test_crear_pedido_rechaza_stock_insuficiente`  
**Commits:** `0bf652a` / `4f6d01c` (regla de dominio) y `27071a2` (repositorio)

### Escenario 6 · Documento de cliente único

```gherkin
Dado un cliente con documento "11112222"
Cuando se intenta registrar otro cliente con el mismo documento
Entonces la restricción UNIQUE impide el commit
```

**Prueba:** `tests/test_persistencia_orm.py::test_documento_de_cliente_es_unico`  
**Commit:** `df33bcd` (modelo) + `27071a2` (repositorio)

---

## 3. Criterios de aceptación técnicos

- [x] ERD con al menos 3 entidades vinculadas y diccionario de datos.
- [x] Modelos ORM con `DeclarativeBase`, `Mapped` y `mapped_column`.
- [x] Relación 1:N `Cliente → Pedido` con `back_populates`.
- [x] Relación 1:N `Pedido → DetallePedido` con cascada.
- [x] Relación N:M `Producto ↔ Etiqueta` con `Table(...)`, `secondary` y `back_populates`.
- [x] Tabla de asociación con datos extra: `DetallePedido`.
- [x] Cascada `all, delete-orphan` en las relaciones dependientes.
- [x] Claves foráneas con `ondelete` y `PRAGMA foreign_keys=ON`.
- [x] Restricciones `UNIQUE`, `CHECK` y `NOT NULL`.
- [x] Fixture `db_session` con `sqlite:///:memory:` y aislamiento por prueba.
- [x] 21 pruebas en verde.
- [x] Ruff sin errores.
- [x] Workflow de GitHub Actions con SQLAlchemy, Ruff y pytest.
- [x] Evidencias RED/GREEN/REFACTOR y PR/merge.

---

## 4. Definition of Done

1. El código está en la rama `feature/PBI-02-orm-persistencia`.
2. `python -m pytest -v` reporta 21 pruebas aprobadas.
3. `python -m ruff check .` reporta `All checks passed!`.
4. El ERD y el diccionario de datos están en el Capítulo 4 del informe.
5. El fixture y la tabla TDD están documentados con hashes reales.
6. El PR fue revisado por el Git Master y fusionado a `main`.
7. El pipeline de GitHub Actions queda en verde con `sqlalchemy` en `requirements.txt`.
8. La demo funcional `python -m src.main --demo` se ejecuta sin errores.

---

## 5. Evidencias

| Evidencia | Ubicación |
|---|---|
| Historia y criterios | Este documento |
| ERD | `docs/erd_optifiber.png`, `docs/erd_optifiber.mmd` |
| Modelos ORM | `src/infraestructura/modelos.py` |
| Fixture | `tests/conftest.py` |
| Pruebas | `tests/test_persistencia_orm.py`, `tests/test_dominio.py`, `tests/test_repositorios.py` |
| Salida de pytest | `docs/evidencias/pytest_final.txt` |
| Salida de Ruff | `docs/evidencias/ruff_final.txt` |
| Demo | `docs/evidencias/demo_final.txt` |
| Commits | `docs/evidencias/commits.md` |
| Informe | `docs/INFORME_CAPITULO_4.md` y `.docx` |
