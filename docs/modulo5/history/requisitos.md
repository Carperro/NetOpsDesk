# Requisitos — Historial de diagnósticos

> Especificación objetivo actualizada con las resoluciones aprobadas para la herramienta 25. La implementación e integración siguen pendientes según el catálogo.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 5, herramienta 25.
- **Propósito:** registrar y consultar el historial de diagnósticos y acciones realizadas en la aplicación.
- **Incluye:** crear entradas manualmente, listar el historial del más nuevo al más antiguo, eliminar una entrada por ID y limpiar todo el historial.
- **No incluye:** captura automática desde las herramientas 1–24 en esta etapa. Una integración futura podrá llamar a la API sin acoplar esos dominios a la persistencia.
- **Familias/protocolos admitidos:** no aplica.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| HIS-F-001 | Crear una entrada | `tool_name`, `action`, `result_status` y `details`; `details` puede omitirse y toma `""` | Se persiste una entrada con ID y fecha de creación | Aprobado; obligatoriedad de `result_status` no especificada |
| HIS-F-002 | Listar entradas | Solicitud sin parámetros | Devuelve las entradas con `ORDER BY created_at DESC, id DESC` | Aprobado |
| HIS-F-003 | Eliminar una entrada | ID de entrada | La entrada se elimina; ID inexistente produce HTTP 422 `not_found` | Aprobado |
| HIS-F-004 | Limpiar el historial | Solicitud sin parámetros | Se eliminan todas las entradas; no afecta otras tablas de `netops.db` | Aprobado |
| HIS-F-005 | Mostrar y agregar entradas desde la interfaz | Usuario consulta o completa el formulario | La interfaz presenta entradas y permite agregar una nueva manualmente | Aprobado en alcance; presentación pendiente |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| HIS-NF-001 | Persistencia | SQLite en la base compartida `netops.db`, tabla `history`; tipos de columna fijados en DEC-HISTORY-03 | Los registros sobreviven al reinicio y las operaciones no alteran tablas de Inventario/IPAM | Aprobado; DEC-018 y DEC-HISTORY-01/03 |
| HIS-NF-002 | Concurrencia | La API utiliza `asyncio.Semaphore(5)` | Al agotarse, responde HTTP 429 `too_many_requests` | Aprobado |
| HIS-NF-003 | Aislamiento | Las herramientas 1–24 no guardan historial automáticamente | La Herramienta 25 permite carga manual; integración futura mediante API | Aprobado; DEC-HISTORY-02 |
| HIS-NF-004 | Orden cronológico | `created_at` es TEXT con valor de `datetime.now().isoformat()` | Listado con `ORDER BY created_at DESC, id DESC` | Aprobado; DEC-HISTORY-03 |

## Criterios de aceptación

- `id` se genera como `INTEGER PRIMARY KEY AUTOINCREMENT`; `tool_name`, `action`, `result_status`, `details` y `created_at` se almacenan como `TEXT`.
- La API requiere `tool_name` y `action`. Si se omite `details`, se usa `""`. La obligatoriedad de `result_status` debe confirmarse antes de implementar.
- Listar devuelve los registros según `ORDER BY created_at DESC, id DESC`; una lista vacía devuelve una colección vacía.
- El timestamp se crea usando `datetime.now().isoformat()`.
- Eliminar un ID inexistente devuelve HTTP 422 `not_found`; al agotarse el semáforo responde HTTP 429 `too_many_requests`.
- Limpiar elimina solo filas de `history` y devuelve éxito sin contenido.
- Las pruebas aíslan la persistencia con SQLite `:memory:`.
- Las herramientas 1–24 no adquieren dependencia del repositorio de History.

## Fuentes y pendientes

- **Decisiones aplicables:** DEC-011 en [registro global](../../fundacional/decision-log.md#dec-011--alcance-del-mvp); DEC-018 en el [registro de Inventario](../../modulo4/inventory/decision-log.md#dec-018--persistencia-sqlite-nativa-con-patrón-repository); DEC-HISTORY-01 a DEC-HISTORY-03 en [registro local](decision-log.md).
- **Fuentes técnicas verificadas:** catálogo, herramienta 25; documentación de DEC-018 para Inventario y su reutilización en IPAM.
- **Pendiente de aprobación o investigación:** confirmar si `result_status` es obligatorio; definir límites de longitud y sobre común de errores de esquema aplicable al Módulo 5.