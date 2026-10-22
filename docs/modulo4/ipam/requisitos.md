# Requisitos — Gestor de direcciones IP (IPAM)

> Estado: alcance y reglas aprobados para la herramienta 17. Hay implementación parcial sin seguimiento por Git; la integración sigue pendiente según el catálogo fundacional.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 4, herramienta 17.
- **Propósito:** registrar direcciones IPv4 y sus asignaciones para consultar su uso, planificar la red y evitar duplicados dentro del inventario almacenado.
- **Incluye:** crear, listar, editar y eliminar registros; validar IPv4 y estado; impedir que una misma dirección figure en más de un registro.
- **No incluye:** descubrimiento automático de hosts, consulta de disponibilidad en la red, DHCP, ni garantía de que una dirección marcada `available` esté realmente libre fuera de los registros guardados.
- **Persistencia:** SQLite nativo compartido en `netops.db`, siguiendo DEC-018 y el patrón Repository de Inventario.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| IPAM-F-001 | Crear un registro | IPv4 y estado admitido; `assigned_to` y `notes` opcionales con default `""` | Se guarda un registro con identificador | Aprobado; flujo presente en copia de trabajo, integración MVP por reconciliar |
| IPAM-F-002 | Listar registros | Solicitud sin filtros | Se devuelven los registros IPAM guardados | Aprobado; flujo presente en copia de trabajo, integración MVP por reconciliar |
| IPAM-F-003 | Editar un registro | Identificador existente y request completo; `assigned_to` y `notes` pueden omitirse | PUT reemplaza todos los campos; opcionales omitidos se guardan como `""` | Aprobado; flujo presente en copia de trabajo, integración MVP por reconciliar |
| IPAM-F-004 | Eliminar un registro | Identificador existente | Se elimina el registro | Aprobado; flujo presente en copia de trabajo, integración MVP por reconciliar |
| IPAM-F-005 | Rechazar duplicados | Una IPv4 ya está registrada | No se crea ni actualiza un segundo registro con esa IP; error `duplicate_ip` | Aprobado; flujo presente en copia de trabajo, integración MVP por reconciliar |
| IPAM-F-006 | Rechazar identificador inexistente | PUT o DELETE con ID ausente | Error `not_found` | Aprobado; flujo presente en copia de trabajo, integración MVP por reconciliar |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| IPAM-NF-001 | Validación | `ip_address` debe ser una IPv4 válida | Una dirección inválida produce `invalid_ip` | Aprobado; regla presente en código de copia de trabajo |
| IPAM-NF-002 | Validación | `status` solo admite `available`, `assigned` o `reserved` | Otro valor produce `invalid_status` | Aprobado; regla presente en código de copia de trabajo |
| IPAM-NF-003 | Integridad | La columna `ip_address` tiene restricción SQLite `UNIQUE` | La base de datos impide duplicados incluso ante escrituras concurrentes; el repositorio los traduce a `duplicate_ip` | Aprobado; repositorio presente |
| IPAM-NF-004 | Concurrencia | La API usa `asyncio.Semaphore(5)` y rechaza solicitudes sin permiso | Si los cinco permisos están ocupados, HTTP 429 `too_many_requests`; el límite es por proceso | Aprobado; implementación pendiente |

## Criterios de aceptación

- Una IPv4 válida con un estado permitido se puede crear y aparece al listar.
- Un valor que no sea IPv4 produce HTTP 422 con `error: "invalid_ip"`.
- Un estado distinto de `available`, `assigned` o `reserved` produce HTTP 422 con `error: "invalid_status"`.
- Registrar una IP que ya existe, tanto en creación como al editar otro registro, produce HTTP 422 `duplicate_ip` y conserva la integridad de los datos.
- PUT o DELETE con un ID inexistente produce HTTP 422 `not_found` por el handler común de `DomainError`.
- `assigned_to` y `notes` se aceptan omitidos y se tratan como strings vacías (`""`).
- PUT reemplaza el registro completo; omitir `assigned_to` o `notes` borra el valor anterior y lo sustituye por `""`.
- Con cinco operaciones ocupando el semáforo, otra solicitud recibe HTTP 429 `too_many_requests` sin esperar en cola.
- La tabla `ip_addresses` contiene `id`, `ip_address`, `status`, `assigned_to` y `notes`; `ip_address` es `UNIQUE`.
- Las operaciones CRUD siguen el contrato de `api-contracts.md`.

## Fuentes y pendientes

- **Decisiones aplicables:** DEC-018 (SQLite nativo y patrón Repository, documentada en [Inventario](../inventory/decision-log.md)); DEC-IPAM-01 y DEC-IPAM-02 ([registro local](decision-log.md)).
- **Fuente de alcance:** [catálogo fundacional, herramienta 17](../../fundacional/catalogo.md).
- **Pendiente de aprobación o investigación:** si una IP se canonicaliza antes de comparar; alcance del semáforo entre workers. No se presume que `available` represente disponibilidad comprobada en la red.
