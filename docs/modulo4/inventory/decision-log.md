# Registro de decisiones — Inventario de dispositivos

Este registro recoge DEC-018 tal como fue indicado por el usuario y decisiones de implementación verificadas en el código. No sustituye el registro fundacional. La búsqueda en `docs/fundacional/decision-log.md` no encontró una entrada global DEC-018; esta copia local deja la decisión trazable para la herramienta.

## Decisiones aprobadas

### DEC-018 — Persistencia SQLite nativa con patrón Repository

- **Estado:** APROBADA según instrucción explícita del usuario.
- **Fecha de registro local:** 2026-10-20. La fecha original de aprobación no fue proporcionada.
- **Contexto:** Inventario requiere persistencia local CRUD sin sumar un ORM para este caso.
- **Decisión:** usar SQLite mediante el módulo estándar `sqlite3`, sin ORM, detrás de la interfaz `InventoryRepository` en `src/netops_desk/repositories/inventory_repository.py`. El dominio recibe el repositorio por parámetro. El repositorio real es `SQLiteInventoryRepository`; las pruebas pueden usar `db_path=":memory:"`.
- **Motivo:** mantener persistencia local y separar reglas de dominio del mecanismo de almacenamiento.
- **Alternativas:** ORM; no elegido para esta herramienta.
- **Consecuencias:** la aplicación crea la base/tablas cuando el repositorio se construye; el default es `netops.db` relativo al directorio de trabajo. FastAPI inyecta el repositorio mediante `get_inventory_repo()`.
- **Aprobación:** decisión DEC-018 declarada como aprobada en la instrucción del usuario para esta auditoría.

## Comportamiento verificado en la implementación

- `DeviceInput` requiere `name` e `ip_address`; `device_type`, `location` y `notes` tienen default `""`; los campos extra están prohibidos.
- `DeviceOutput` contiene `id`, `name`, `ip_address`, `device_type`, `location` y `notes`.
- El dominio produce `invalid_name`, `invalid_ip` y `not_found` como `DomainError`; el handler global asigna HTTP 422 a todos los `DomainError`.
- La lista se ordena por `id DESC`.
- El PUT usa el mismo modelo que POST. Los campos opcionales omitidos llegan al dominio como strings vacías y reemplazan los valores previos.

## Discrepancias de estado que requieren seguimiento separado

- **Archivo de base de datos:** la expectativa comunicada dice que `netops.db` está ignorada por Git. En el árbol auditado `git ls-files` devuelve `netops.db` y `.gitignore` no contiene una regla para él. Este pase no modifica `.gitignore`, el archivo DB ni el índice.
- **Catálogo:** `docs/fundacional/catalogo.md` todavía marca la herramienta 16 como pendiente de desarrollo e integración, aunque se encontraron dominio, repositorio, rutas, frontend y tests. Este pase no cambia el catálogo.
- **Registro global:** la búsqueda local no encontró DEC-018 en el decision log fundacional; por eso queda documentada aquí como la aprobación indicada por el usuario, pendiente de reconciliar en la fuente global si corresponde.
