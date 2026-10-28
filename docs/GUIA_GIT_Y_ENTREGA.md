# Guía de Git, GitHub, CI y entrega

Esta guía explica cómo publicar el proyecto **OptiFiber FTTH**, abrir el Pull Request del PBI-02, verificar GitHub Actions y preparar la entrega del Trabajo Colaborativo N° 04.

---

## 1. Estado del repositorio local

El proyecto ya tiene un repositorio Git inicializado con:

- Rama `main` con la estructura base.
- Rama `feature/PBI-02-orm-persistencia` con los ciclos TDD.
- Merge `--no-ff` hacia `main` (PR #2) con hash **`329b4ea`**.
- Tag `pbi-02-v1.0`.

Verificar:

```powershell
cd "C:\Users\estudiante\Documents\Proyecto predeterminado\optifiber-ftth"
git status
git log --graph --oneline --decorate --all
git tag
```

La secuencia esperada es:

```text
*   merge (main) Merge pull request #2 ...
|\
| * 9268085 refactor: (REFACTOR) ...
| * 27071a2 feat: (GREEN) repositorios...
| * ...
| * b292e8c test: (RED) ...
|/
* cc4e5e7 chore: crear estructura base...
```

---

## 2. Crear el repositorio en GitHub

### Opción A · Desde la web

1. Ingresar a <https://github.com/new>.
2. Nombre: `optifiber-ftth`.
3. Visibilidad: **Private** (recomendado para trabajos académicos) o **Public**.
4. **No** marcar “Add a README”, “Add .gitignore” ni “Choose a license” (el repositorio local ya los tiene).
5. Crear el repositorio.

### Opción B · Con GitHub CLI

```powershell
gh auth login
gh repo create optifiber-ftth --private --source . --remote origin --push
```

Si se usa la opción B, el `--push` sube la rama actual. Verificar que sea `main`:

```powershell
git branch --show-current
```

---

## 3. Publicar las ramas y el tag

```powershell
git remote add origin https://github.com/TU_USUARIO/optifiber-ftth.git
git push -u origin main
git push origin feature/PBI-02-orm-persistencia
git push --tags
```

Comprobar en GitHub:

- `main` contiene el merge y la documentación.
- `feature/PBI-02-orm-persistencia` conserva los commits RED/GREEN/REFACTOR.
- El tag `pbi-02-v1.0` apunta al merge.
- La pestaña **Actions** muestra el workflow **CI - Calidad y Pruebas**.

---

## 4. Pull Request #2

### Caso A · El repositorio local ya está fusionado

El merge local se hizo con el mensaje `Merge pull request #2 from feature/PBI-02-orm-persistencia`. En GitHub se puede evidenciar con:

- El commit de merge en `main`.
- La rama `feature/PBI-02-orm-persistencia` publicada.
- El tag `pbi-02-v1.0`.
- El historial `git log --graph`.

### Caso B · El docente exige un PR abierto y fusionado en GitHub

Si el repositorio remoto todavía no tiene el merge, publicar primero la rama del PBI y abrir el PR **antes** de subir `main`:

```powershell
git push origin feature/PBI-02-orm-persistencia
```

En GitHub:

1. **Pull requests → New pull request**.
2. Base: `main`; compare: `feature/PBI-02-orm-persistencia`.
3. Título: `PBI-02: persistencia ORM, cascada y pruebas con fixtures`.
4. Descripción: usar la plantilla de la sección 5.
5. Crear el PR y esperar los checks **Ruff** y **Pytest**.
6. Revisar el código y aprobar.
7. **Merge pull request → Create merge commit** (no squash, para conservar la secuencia TDD).
8. Actualizar el repositorio local:

```powershell
git checkout main
git pull origin main
```

> Si `main` ya fue publicado con el merge local, el PR aparecerá sin diferencias. En ese caso, la evidencia del PR es el commit de merge y el historial; para una demostración literal del flujo, crear un repositorio nuevo y publicar primero la rama del PBI.

---

## 5. Plantilla de descripción del PR

```markdown
## PBI-02 · Persistencia de clientes, pedidos y catálogo FTTH

### Qué incluye
- ERD de 6 entidades con relaciones 1:N y N:M.
- Modelos SQLAlchemy 2.x con `Mapped`, `mapped_column` y `relationship`.
- Cascada `all, delete-orphan` en Cliente→Pedido y Pedido→DetallePedido.
- Tabla de asociación `producto_etiqueta` con `secondary`.
- Fixture `db_session` con `sqlite:///:memory:`.
- 21 pruebas de persistencia, dominio y repositorios.
- CLI funcional y demo automática.
- Workflow de GitHub Actions con Ruff + pytest.

### Evidencias
- `docs/evidencias/pytest_final.txt`: 21 passed.
- `docs/evidencias/ruff_final.txt`: All checks passed.
- `docs/evidencias/commits.md`: secuencia RED/GREEN/REFACTOR.
- `docs/INFORME_CAPITULO_4.md`: Capítulo 4 completo.

### Checklist
- [x] Pruebas en verde.
- [x] Ruff sin errores.
- [x] SQLAlchemy en requirements.txt.
- [x] Documentación actualizada.
```

---

## 6. GitHub Actions y protección de rama

El workflow `.github/workflows/ci.yml` se ejecuta en:

- Push a `main`, `dev` y `feature/**`.
- Pull requests hacia `main` y `dev`.

Pasos:

1. Descarga el repositorio.
2. Configura Python 3.12.
3. Instala `requirements.txt` (incluye SQLAlchemy, pytest y Ruff).
4. Ejecuta `ruff check .`.
5. Ejecuta `pytest -v`.

### Configurar protección de `main`

1. GitHub → **Settings → Branches → Add branch protection rule**.
2. Branch name pattern: `main`.
3. Activar:
   - **Require a pull request before merging**.
   - **Require status checks to pass before merging**.
   - Seleccionar el check `Ruff + Pytest (Python 3.12)`.
4. Guardar.

### Verificar el pipeline localmente

```powershell
python -m pip install -r requirements.txt
python -m ruff check .
python -m pytest -v
```

Resultado esperado: `All checks passed!` y `21 passed`.

---

## 7. Evidencias para la entrega

Capturar y guardar en `docs/evidencias/` (o en el informe):

| Evidencia | Cómo obtenerla | Archivo sugerido |
|---|---|---|
| Suite completa | `python -m pytest -v` | `pytest_final.txt` |
| Ruff | `python -m ruff check .` | `ruff_final.txt` |
| Demo funcional | `python -m src.main --demo` | `demo_final.txt` |
| Historial TDD | `git log --graph --oneline --all` | `git_log.txt` |
| Commits por autor | `git log --pretty=format:"%h %an %s"` | `commits.md` |
| Estado del repo | `git status` | captura |
| GitHub Actions | Pestaña Actions con el check verde | captura |
| Pull Request | Página del PR #2 | captura |
| ERD | `docs/erd_optifiber.png` | incluido |

Comandos:

```powershell
python -m pytest -v 2>&1 | Out-File docs/evidencias/pytest_final.txt -Encoding utf8
python -m ruff check . 2>&1 | Out-File docs/evidencias/ruff_final.txt -Encoding utf8
python -m src.main --demo 2>&1 | Out-File docs/evidencias/demo_final.txt -Encoding utf8
git log --graph --oneline --decorate --all 2>&1 | Out-File docs/evidencias/git_log.txt -Encoding utf8
```

---

## 8. Checklist de entrega

- [ ] Repositorio creado y visible para el docente.
- [ ] `main` actualizado y con el merge del PBI-02.
- [ ] Rama `feature/PBI-02-orm-persistencia` publicada.
- [ ] Tag `pbi-02-v1.0` publicado.
- [ ] GitHub Actions en verde (Ruff + Pytest).
- [ ] PR #2 revisado y fusionado.
- [ ] `docs/INFORME_CAPITULO_4.md` completo.
- [ ] `docs/Informe_Capitulo_4_OptiFiber.docx` generado.
- [ ] `docs/erd_optifiber.png` incluido.
- [ ] `docs/evidencias/pytest_final.txt` con 21 passed.
- [ ] `docs/evidencias/ruff_final.txt` con All checks passed.
- [ ] `docs/DISTRIBUCION_EQUIPO.md` con los 4 integrantes y roles.
- [ ] `docs/PBI-02.md` con Gherkin y DoD.
- [ ] Demo `python -m src.main --demo` ejecutada en la sustentación.

---

## 9. Solución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'src'` | Se ejecutó fuera de la raíz del proyecto. | `cd optifiber-ftth` y ejecutar `python -m ...`. |
| `no such table: clientes` | No se llamó a `Base.metadata.create_all` o faltó importar un modelo. | Usar `inicializar_db(engine)` y verificar que `modelos.py` importe todas las entidades. |
| `ModuleNotFoundError: sqlalchemy` | Dependencias no instaladas o venv inactivo. | Activar `.venv` y `pip install -r requirements.txt`. |
| `pytest` no encuentra pruebas | Se ejecutó desde otra carpeta. | Ejecutar desde la raíz; `pyproject.toml` define `testpaths = ["tests"]`. |
| `IntegrityError: NOT NULL constraint failed` | Se intentó borrar una entidad sin cascada. | Revisar `cascade="all, delete-orphan"` y `PRAGMA foreign_keys=ON`. |
| `FOREIGN KEY constraint failed` | `RESTRICT` protege productos/categorías con historial. | Eliminar primero los detalles o cambiar la política de negocio. |
| La consola muestra caracteres raros | Codificación de Windows. | La CLI reconfigura `sys.stdout` a UTF-8; usar Windows Terminal o PowerShell 7. |
| El estudiante no puede activar el venv | Política de ejecución de PowerShell. | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. |

---

## 10. Comandos de demostración rápida

```powershell
# 1. Calidad
python -m ruff check .
python -m pytest -v

# 2. Demo funcional (no modifica la base persistente)
python -m src.main --demo

# 3. Menú interactivo (crea data/optifiber.db)
python -m src.main

# 4. Historial TDD
git log --graph --oneline --decorate --all

# 5. Estado del repositorio
git status
git remote -v
```
