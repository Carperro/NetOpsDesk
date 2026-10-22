# Arquitectura — Gestor de direcciones IP (IPAM)

> Estado: implementación presente en la copia de trabajo el 2026-10-20, pero sin seguimiento por Git. Dominio, repositorio, modelos, rutas, pruebas y recursos frontend existen; `api/main.py` está modificado para registrar las rutas y la página. Estos cambios no forman parte del commit documental. El catálogo todavía marca pendiente la integración de la herramienta.

## Componentes y responsabilidades

| Capa/componente | Ubicación | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/ipam.py` (presente sin seguimiento) | Validar IPv4/estado, aplicar CRUD mediante repositorio y producir errores de dominio | `ipaddress`, `DomainError` y protocolo del repositorio; sin FastAPI ni SQL |
| Repositorio | `src/netops_desk/repositories/ipam_repository.py` (presente sin seguimiento) | Persistir y consultar registros; usar `UNIQUE` y traducir duplicados a `DomainError(duplicate_ip)` | `sqlite3` y esquema de persistencia |
| API | `src/netops_desk/api/models/ipam.py`, `src/netops_desk/api/routes/ipam.py` (presentes sin seguimiento); `api/main.py` modificado | Adaptar las cuatro operaciones HTTP al dominio, inyectar el repositorio y serializar respuestas; el router está registrado en la copia de trabajo | FastAPI/Pydantic, dominio y repositorio |
| Interfaz | `src/netops_desk/static/tools/ipam.html`, `static/js/ipam.js`, `static/css/ipam.css` (presentes sin seguimiento) | Crear, consultar, editar y eliminar registros; presentar errores y resultados | API y recursos locales |
| Pruebas | `tests/test_ipam_domain.py`, `tests/test_ipam_repository.py`, `tests/test_api_ipam.py` (presentes sin seguimiento) | FakeRepo para dominio, SQLite `:memory:` y contrato HTTP; no ejecutadas en esta revisión | Pytest, TestClient y dobles de prueba |

## Flujo principal objetivo

1. La ruta existente valida el request con Pydantic; el dominio valida IPv4 y estado como invariantes de negocio.
2. La capa API obtiene el repositorio mediante una dependencia inyectable, siguiendo DEC-018 y el patrón de Inventario.
3. El dominio ejecuta CRUD a través del protocolo del repositorio, sin conocer HTTP ni SQL.
4. El repositorio usa consultas SQLite parametrizadas y la tabla `ip_addresses` dentro de `netops.db`.
5. `ip_address` tiene una restricción `UNIQUE`. Ante una violación por inserción o actualización, el repositorio traduce `sqlite3.IntegrityError` a `DomainError` con código `duplicate_ip`.
6. El handler global convierte errores de dominio a HTTP 422 y al sobre `{ "error": "...", "detail": "..." }`. El router está registrado en la copia de trabajo de `create_app()`.

## Persistencia

La tabla contiene `id`, `ip_address`, `status`, `assigned_to` y `notes`. El repositorio visible declara `id INTEGER PRIMARY KEY AUTOINCREMENT`, `ip_address TEXT NOT NULL UNIQUE`, `status TEXT NOT NULL` y `assigned_to TEXT`/`notes TEXT` nullable, sin defaults SQL. El dominio existente recorta espacios de IP, destino y notas, y normaliza el estado a minúsculas; para destino y notas omitidos asigna `""` antes de llamar al repositorio.

DEC-018 fija SQLite nativo (`sqlite3`), sin ORM, repositorio inyectable y `:memory:` para pruebas. La dependencia de API será un proveedor equivalente a `get_inventory_repo()`; el nombre concreto del proveedor IPAM se define al implementar.

## Límites y errores

- **Validación observada en dominio:** `ip_address` se recorta y valida con `ipaddress.IPv4Address`; `status` se recorta y normaliza a minúsculas antes de aceptar `available`, `assigned` o `reserved`. No se define una regla condicional entre estado y `assigned_to`.
- **Campos opcionales:** `assigned_to` y `notes` son strings opcionales con default `""`. En PUT se reemplazan todos los campos; si se omite alguno de estos dos, se guarda `""`.
- **Errores de dominio:** `invalid_ip`, `invalid_status`, `duplicate_ip` y `not_found` se traducen a HTTP 422 por el handler global.
- **Integridad concurrente:** la restricción `UNIQUE` es la protección final ante escrituras simultáneas; una consulta previa no la sustituye.
- **Privacidad:** `assigned_to` y `notes` pueden contener datos identificables u operativos. No incluirlos en logs innecesarios ni exponerlos fuera del flujo autorizado.
- **Concurrencia API aprobada:** la ruta debe usar `asyncio.Semaphore(5)` y, si los cinco permisos están ocupados, rechazar inmediatamente con HTTP 429 `too_many_requests`. La ruta presente aún no implementa el semáforo ni ese estado. El límite es por proceso/event loop; el comportamiento global con varios workers no está aprobado.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** DEC-018 (SQLite y Repository); DEC-IPAM-01 (unicidad en base); DEC-IPAM-02 (estados cerrados); DEC-IPAM-03 (campos opcionales y reemplazo PUT); DEC-IPAM-04 (semáforo y saturación 429).
- **Persistencia:** no se incorpora ORM. El dominio queda desacoplado del motor mediante el repositorio.
- **Conectividad:** CRUD local mediante SQLite; no requiere servicio externo.
- **Despliegue:** el semáforo aprobado aún no está implementado. Cuando se incorpore, limitará cada proceso; para asegurar un máximo de cinco operaciones a nivel de despliegue se necesitaría un worker o coordinación compartida.

## Estado y referencias

- [Requisitos](requisitos.md), [contrato API](api-contracts.md), [decisiones](decision-log.md) y [estrategia de pruebas](test-strategy.md).
- [Arquitectura de Inventario](../inventory/arquitectura.md), patrón SQLite y Repository de DEC-018.
- [Catálogo fundacional](../../fundacional/catalogo.md): herramienta 17 pendiente de desarrollo e integración.
- Los archivos IPAM de dominio, repositorio, modelos, ruta, pruebas y frontend observados están sin seguimiento por Git; `src/netops_desk/api/main.py` está modificado. Ninguno forma parte de este cambio documental.
- `netops.db` estaba trackeado en Git y no estaba cubierto por `.gitignore`; este cambio lo retira del índice y añade una regla de exclusión. El archivo local se conserva.
