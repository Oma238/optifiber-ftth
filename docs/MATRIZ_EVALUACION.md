# Matriz de evaluación · Trabajo Colaborativo N° 04

**Empresa:** OPTIFIBER · venta de productos FTTH  
**PBI:** PBI-02 · Persistencia de clientes, pedidos y catálogo FTTH  
**Rama:** `feature/PBI-02-orm-persistencia`  
**Equipo:** Omar Huallpayunca · Kevin Llerena · Amaru Ai-me · Julio Diaz

---

## 1. Checklist oficial del docente

| N° | Criterio de verificación | Evidencia concreta | Archivo / ubicación | Estado |
|---:|---|---|---|---|
| 1 | **Modelo ERD e infraestructura ORM:** esquema relacional en la Sección 4.1 y código funcional de los modelos. | 6 entidades, 5 relaciones, claves y restricciones; 21 pruebas. | `docs/erd_optifiber.png`, `docs/INFORME_CAPITULO_4.md` §4.1, `src/infraestructura/modelos.py` | ✅ |
| 2 | **Fixture de base de datos en memoria:** configuración aislada para pruebas herméticas. | `create_engine("sqlite:///:memory:")`, `StaticPool`, `PRAGMA foreign_keys=ON`, `scope="function"`. | `tests/conftest.py` | ✅ |
| 3 | **Pruebas de persistencia:** relación 1:N y eliminación en cascada en verde. | `21 passed`; casos 1:N, cascada, N:M y repositorios. | `tests/`, `docs/evidencias/pytest_final.txt` | ✅ |
| 4 | **Historial de commits Git:** secuencia RED → GREEN → REFACTOR en la rama del PBI. | 13 commits con autores del equipo, incluyendo 5 ciclos RED/GREEN. | `git log --graph`, `docs/evidencias/commits.md` | ✅ |
| 5 | **Pull Request y GitHub Actions:** checks de Ruff y pytest en verde, SQLAlchemy en requirements. | Workflow `ci.yml`; PR #2; merge `329b4ea`; tag `pbi-02-v1.0`; `SQLAlchemy` en `requirements.txt`. | `.github/workflows/ci.yml`, `requirements.txt`, `docs/GUIA_GIT_Y_ENTREGA.md` | ✅ |
| 6 | **Capítulo 4 del Informe:** secciones 4.1, 4.2 y 4.3 completas. | ERD, diccionario de datos, código ORM, fixture, tabla TDD y conclusiones. | `docs/INFORME_CAPITULO_4.md`, `docs/Informe_Capitulo_4_OptiFiber.docx` | ✅ |

---

## 2. Cobertura de pruebas

| Tipo | Archivo | Pruebas | Estado |
|---|---|---:|---|
| Persistencia ORM | `tests/test_persistencia_orm.py` | 5 | ✅ |
| Dominio puro | `tests/test_dominio.py` | 10 | ✅ |
| Repositorios | `tests/test_repositorios.py` | 6 | ✅ |
| **Total** | — | **21** | ✅ |

---

## 3. Commits y autores

| Integrante | Commits | Rol |
|---|---|---|
| Omar Huallpayunca | `cc4e5e7`, documentación, merge | Git Master + PO/SM |
| Kevin Llerena | `0bf652a`, `4f6d01c`, `27071a2` | Lead Backend |
| Amaru Ai-me | `c368e49`, `72e423d`, `df33bcd` | Database & ORM |
| Julio Diaz | `c394468`, `b292e8c`, `33febea`, `e397f22`, `417ed0f`, `9268085` | DevOps & QA + Frontend |

---

## 4. Evidencias de ejecución

| Comando | Resultado | Archivo |
|---|---|---|
| `python -m pytest -v` | `21 passed` | `docs/evidencias/pytest_final.txt` |
| `python -m ruff check .` | `All checks passed!` | `docs/evidencias/ruff_final.txt` |
| `python -m src.main --demo` | Catálogo, pedido con descuento y cascada verificada | `docs/evidencias/demo_final.txt` |
| `git log --graph --oneline --all` | Secuencia TDD completa | `docs/evidencias/commits.md` |

---

## 5. Firma de conformidad del equipo

| Integrante | Rol | Conformidad |
|---|---|---|
| Huallpayunca Carrion Omar Sebastian | Git Master + PO/SM | ☐ |
| Kevin Jesus Llerena Fernandez | Lead Backend Engineer | ☐ |
| Amaru Josue Ai-me Yunguri | Database & ORM Specialist | ☐ |
| Julio Cesar Diaz Tito | DevOps & QA + Frontend/UX | ☐ |

> Completar las casillas al momento de la entrega. La matriz resume las evidencias que se revisarán en mesa.
