# Distribución de funciones · Equipo OptiFiber

**Trabajo Colaborativo N° 04 · Persistencia de Datos, Mapeo ORM y Pruebas con Fixtures**  
**Empresa:** OPTIFIBER · venta de productos FTTH  
**Equipo:** 4 integrantes (se cubren los 5 roles del instructivo)

---

## 1. Asignación de roles

| N° | Integrante | Rol asumido | Rol(es) del instructivo | GitHub sugerido |
|---:|---|---|---|---|
| 1 | **Huallpayunca Carrion Omar Sebastian** | Git Master + Product Owner / Scrum Master | Product Owner / Scrum Master | `@omarhuallpayunca` |
| 2 | **Kevin Jesus Llerena Fernandez** | Lead Backend Engineer | Lead Backend Engineer | `@kevinllerena` |
| 3 | **Amaru Josue Ai-me Yunguri** | Database & ORM Specialist | Database & ORM Specialist | `@amaruaime` |
| 4 | **Julio Cesar Diaz Tito** | DevOps & QA Engineer + Frontend/UX/UI Engineer | DevOps & QA + Frontend/UX/UI | `@juliodiaz` |

> **Criterio de combinación:** el instructivo está diseñado para 5 integrantes. Como el equipo tiene 4, se fusionaron los roles que comparten herramientas y momentos del taller: PO/SM con Git Master (Omar) y DevOps/QA con Frontend/UX (Julio). Ningún rol del instructivo queda sin responsable.

> **Importante:** los usuarios de GitHub son sugeridos. Antes de publicar, reemplazarlos por los usuarios reales en el README, este documento y el informe.

---

## 2. Responsabilidades por fase del taller

### Fase 1 · ERD, roles y PBI de persistencia (25 min)

| Actividad | Responsable principal | Apoyo | Entregable |
|---|---|---|---|
| Revisar el instructivo y definir el alcance del PBI-02 | Omar | Todo el equipo | PBI-02 actualizado |
| Diseñar el ERD de OPTIFIBER con al menos 3 entidades | Amaru | Kevin | `docs/erd_optifiber.png`, `docs/erd_optifiber.mmd` |
| Validar que los campos del ORM coincidan con el flujo comercial (catálogo, cliente, pedido) | Julio | Amaru | Observaciones incorporadas al ERD |
| Revisar separación de capas y reglas de negocio | Kevin | Omar | Lista de reglas: stock, total, descuento, DNI/RUC |
| Crear la rama `feature/PBI-02-orm-persistencia` y registrar el PBI en progreso | Omar | Julio | Rama local + `docs/PBI-02.md` |
| Definir la tabla de asociación N:M | Amaru | Kevin | `producto_etiqueta` y `DetallePedido` |

### Fase 2 · Estructura de persistencia (10 min)

| Actividad | Responsable | Archivo(s) |
|---|---|---|
| Crear la clase `Base` declarativa | Amaru | `src/infraestructura/modelos.py` |
| Configurar `requirements.txt` con SQLAlchemy | Julio | `requirements.txt` |
| Crear el fixture `db_session` con `sqlite:///:memory:` | Julio | `tests/conftest.py` |
| Verificar que el pipeline instale SQLAlchemy | Julio | `.github/workflows/ci.yml` |
| Revisar que `src/dominio` siga sin dependencias de BD | Kevin | `src/dominio/` |
| Registrar el commit de configuración | Omar | `c394468` |

### Fase 3 · Ciclos TDD (40 min)

| Ciclo | Responsable de la prueba (RED) | Responsable del modelo (GREEN) | Responsable del REFACTOR | Evidencia |
|---|---|---|---|---|
| 1. Cliente 1:N Pedido | Julio | Amaru | Julio | `b292e8c` → `c368e49` |
| 2. Cascada Cliente → Pedido | Julio | Amaru | Julio | `33febea` → `72e423d` |
| 3. N:M Producto–Etiqueta y DetallePedido | Julio | Amaru | Julio | `e397f22` → `df33bcd` |
| 4. Reglas de dominio | Kevin | Kevin | Julio | `0bf652a` → `4f6d01c` |
| 5. Repositorios y pedidos | Julio | Kevin | Julio | `417ed0f` → `27071a2` |
| Cierre Ruff | Julio | — | Julio | `9268085` |

**Regla de trabajo:** nadie hace merge de su propio código sin revisión de otro integrante. El Git Master revisa el PR y aprueba el merge.

### Fase 4 · Evidencias e informe (15 min)

| Actividad | Responsable | Entregable |
|---|---|---|
| Completar 4.1 (ERD) | Amaru | `docs/INFORME_CAPITULO_4.md` §4.1 |
| Completar 4.2 (código ORM) | Amaru + Kevin | §4.2 |
| Completar 4.3 (fixture y TDD) | Julio | §4.3 + `docs/evidencias/` |
| Redactar conclusiones y checklist | Omar + Kevin | §4.4 y §4.5 |
| Generar el DOCX y revisar formato | Omar | `docs/Informe_Capitulo_4_OptiFiber.docx` |
| Revisar el PR y fusionar a `main` | Omar | Merge commit / PR #2 |

---

## 3. Aportes concretos por integrante

### Omar Sebastian Huallpayunca Carrion · Git Master + PO/SM

- Creó el repositorio, la estructura base y la rama `feature/PBI-02-orm-persistencia`.
- Registró y priorizó el **PBI-02** con historia de usuario y criterios Gherkin.
- Revisó la separación de capas y la coherencia del informe.
- Aprobó el Pull Request y ejecutó el merge `--no-ff` hacia `main`.
- Generó el informe Word y coordinó la entrega.
- **Commits:** `cc4e5e7` (estructura), commits de documentación y merge final.

### Kevin Jesus Llerena Fernandez · Lead Backend Engineer

- Implementó las reglas de negocio puras en `src/dominio/servicios.py`:
  - subtotal con redondeo decimal;
  - descuento por volumen del 5 % desde S/ 1 500;
  - validación de stock, cantidades y documento DNI/RUC.
- Implementó la capa de repositorios `ClienteRepositorio`, `CatalogoRepositorio` y `PedidoRepositorio`.
- Verificó que `src/dominio` no importe SQLAlchemy.
- Revisó que la CLI no contenga reglas de negocio duplicadas.
- **Commits:** `0bf652a`, `4f6d01c`, `27071a2`.

### Amaru Josue Ai-me Yunguri · Database & ORM Specialist

- Diseñó el ERD y el diccionario de datos.
- Implementó `Base` y las 6 entidades: `ClienteModel`, `CategoriaModel`, `EtiquetaModel`, `ProductoModel`, `PedidoModel`, `DetallePedidoModel`.
- Mapeó claves foráneas, relaciones `back_populates`, `secondary` y `cascade="all, delete-orphan"`.
- Definió restricciones `UNIQUE`, `CHECK` y la tabla `producto_etiqueta`.
- **Commits:** `c368e49`, `72e423d`, `df33bcd`.

### Julio Cesar Diaz Tito · DevOps & QA + Frontend/UX

- Configuró `tests/conftest.py` con SQLite en memoria, `StaticPool` y `PRAGMA foreign_keys=ON`.
- Escribió las pruebas RED/GREEN de persistencia, dominio y repositorios.
- Configuró `.github/workflows/ci.yml` para instalar SQLAlchemy y ejecutar Ruff + pytest.
- Implementó la CLI y el flujo de demostración (`--demo`).
- Capturó las evidencias de pytest, Ruff, demo y commits.
- **Commits:** `c394468`, `b292e8c`, `33febea`, `e397f22`, `417ed0f`, `9268085`.

---

## 4. Distribución porcentual y evidencias de participación

| Integrante | % de aporte | Evidencia principal |
|---|---:|---|
| Omar Huallpayunca | 25 % | Estructura, PBI, revisión, merge, DOCX |
| Kevin Llerena | 25 % | Dominio y repositorios (3 commits) |
| Amaru Ai-me | 25 % | ERD y modelos ORM (3 commits) |
| Julio Diaz | 25 % | Fixture, pruebas, CI, CLI y evidencias (6 commits) |

La distribución es equivalente porque cada integrante lidera una capa del proyecto y participa en la revisión de las demás. Los commits tienen autoría explícita y los archivos modificados permiten verificar el aporte.

---

## 5. Guion breve para la exposición

| Pregunta probable | Quién responde | Idea clave |
|---|---|---|
| ¿Cuál es el PBI y qué problema resuelve? | Omar | Registrar clientes, pedidos y catálogo FTTH con historial y control de stock. |
| ¿Por qué eligieron esas entidades? | Amaru | Reflejan el flujo real: cliente → pedido → detalle → producto → categoría/etiqueta. |
| ¿Dónde está la relación N:M? | Amaru | `Producto` N:M `Etiqueta` con `producto_etiqueta`; `DetallePedido` resuelve Pedido–Producto con datos extra. |
| ¿Cómo funciona la cascada? | Amaru | `cascade="all, delete-orphan"` en Cliente→Pedido y Pedido→Detalle; al borrar el cliente desaparecen sus pedidos y detalles. |
| ¿Dónde está la lógica de negocio? | Kevin | En `src/dominio/servicios.py`, sin SQLAlchemy; los repositorios solo persisten. |
| ¿Cómo se calcula el total? | Kevin | Subtotal por línea con Decimal, suma y descuento del 5 % desde S/ 1 500. |
| ¿Cómo garantizan pruebas herméticas? | Julio | Fixture `db_session` con `sqlite:///:memory:` y una sesión nueva por prueba. |
| ¿Cómo se ejecuta la calidad? | Julio | `ruff check .` y `pytest -v` localmente y en GitHub Actions. |
| ¿Qué evidencia hay del TDD? | Omar | Secuencia de commits RED → GREEN → REFACTOR en la rama del PBI. |

---

## 6. Checklist de participación

- [x] Los 4 integrantes aparecen como autores de commits.
- [x] Cada integrante tiene al menos un entregable propio.
- [x] El PBI-02 está registrado y relacionado con pruebas.
- [x] El PR tiene revisión y merge del Git Master.
- [x] El informe incluye la tabla de roles y la distribución de funciones.
- [x] Las evidencias están en `docs/evidencias/`.
