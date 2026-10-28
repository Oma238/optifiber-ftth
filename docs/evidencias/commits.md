# Resumen de commits del PBI-02

| Etapa | Hash corto | Mensaje | Autor |
|---|---|---|---|
| Estructura | `cc4e5e7` | chore: crear estructura base del proyecto OptiFiber FTTH | Omar Huallpayunca |
| Fixture + Base | `c394468` | chore: configurar fixture db_session y clase Base para PBI-02 | Julio Diaz |
| RED ciclo 1 | `b292e8c` | test: (RED) verificar guardar cliente con sus pedidos en la capa ORM | Julio Diaz |
| GREEN ciclo 1 | `c368e49` | feat: (GREEN) implementar modelos ORM Cliente y Pedido con relacion 1:N | Amaru Ai-me |
| RED ciclo 2 | `33febea` | test: (RED) verificar eliminacion en cascada de pedidos al borrar cliente | Julio Diaz |
| GREEN ciclo 2 | `72e423d` | feat: (GREEN) agregar cascade all, delete-orphan en relacion Cliente-Pedidos | Amaru Ai-me |
| RED ciclo 3 | `e397f22` | test: (RED) verificar relacion N:M Producto-Etiqueta y detalles de pedido | Julio Diaz |
| GREEN ciclo 3 | `df33bcd` | feat: (GREEN) implementar catalogo, etiquetas y detalle de pedido con N:M | Amaru Ai-me |
| RED dominio | `0bf652a` | test: (RED) verificar reglas de negocio puras del dominio | Kevin Llerena |
| GREEN dominio | `4f6d01c` | feat: (GREEN) implementar servicios de dominio para totales, descuento y stock | Kevin Llerena |
| RED repositorios | `417ed0f` | test: (RED) verificar repositorios y persistencia de pedidos | Julio Diaz |
| GREEN repositorios | `27071a2` | feat: (GREEN) implementar repositorios, seed y CLI funcional de OptiFiber | Kevin Llerena |
| REFACTOR | `9268085` | refactor: (REFACTOR) verificar suite con ruff y ordenar imports | Julio Diaz |

Los hashes completos se pueden consultar con:

```powershell
git log --graph --oneline --decorate --all
git log --pretty=format:"%H  %an  %s"
```
