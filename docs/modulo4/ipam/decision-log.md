# Registro de decisiones — Gestor de direcciones IP (IPAM)

Este registro contiene las decisiones aprobadas para la herramienta 17. DEC-018 se define en el contexto de Inventario y se reutiliza; este archivo no sustituye el registro fundacional.

## Decisiones

### DEC-IPAM-01 — Restricción única para direcciones

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20 (registro documental; la fecha original de aprobación no se especificó).
- **Contexto:** IPAM debe impedir que dos registros representen la misma dirección.
- **Decisión:** la columna `ip_address` de `ip_addresses` tendrá una restricción `UNIQUE`. El repositorio capturará `sqlite3.IntegrityError` de una inserción o actualización duplicada y la traducirá a `DomainError` con código `duplicate_ip`.
- **Motivo:** la propia base de datos garantiza la integridad incluso si dos operaciones concurrentes pasan una comprobación previa al mismo tiempo.
- **Alternativas:** consultar si ya existe antes de escribir no se considera garantía suficiente por sí sola.
- **Consecuencias:** `duplicate_ip` se traduce a HTTP 422 mediante el handler global. La restricción debe aplicarse también al actualizar la dirección de un registro.
- **Aprobación:** solicitud del usuario para crear la documentación de IPAM.

### DEC-IPAM-02 — Estados cerrados y validados en dominio

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20 (registro documental; la fecha original de aprobación no se especificó).
- **Contexto:** los registros necesitan expresar si una dirección está libre en el inventario, asignada o reservada.
- **Decisión:** `status` solo admite `available`, `assigned` y `reserved`; la validación se aplica en el dominio además de la validación de forma en la API.
- **Motivo:** mantener un conjunto estable de estados y no aceptar etiquetas arbitrarias.
- **Alternativas:** estados libres no aprobados.
- **Consecuencias:** un valor fuera del conjunto produce `DomainError` con código `invalid_status`, HTTP 422. El estado `available` describe el registro; no demuestra que la IP esté libre en la red real.
- **Aprobación:** solicitud del usuario para crear la documentación de IPAM.

### DEC-018 — Persistencia local con SQLite y Repository

- **Estado:** APLICABLE a IPAM según la decisión aprobada para Inventario.
- **Contexto:** las herramientas de gestión de inventario requieren persistencia local intercambiable y reglas de dominio separadas del almacenamiento.
- **Decisión:** reutilizar SQLite nativo (`sqlite3`), sin ORM, el archivo compartido `netops.db` y el patrón Repository descrito en [DEC-018 de Inventario](../inventory/decision-log.md).
- **Motivo:** compartir la arquitectura de persistencia aprobada para la herramienta 16.
- **Consecuencias:** el repositorio IPAM tendrá su propia tabla `ip_addresses`; las pruebas usarán una base SQLite en memoria (`:memory:`) para aislar los datos.
- **Aprobación:** DEC-018 aprobada por el usuario para Inventario y reutilización solicitada explícitamente para IPAM.

### DEC-IPAM-03 — Campos opcionales y reemplazo completo en PUT

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** los registros incluyen destino de asignación y notas, y el endpoint de actualización usa PUT.
- **Decisión:** `assigned_to` y `notes` son strings opcionales con default `""`. PUT reemplaza todos los campos del registro; al omitir cualquiera de esos campos, su valor previo se sustituye por `""`.
- **Motivo:** hacer explícita y determinista la semántica del request completo.
- **Alternativas:** tratar PUT como PATCH o conservar silenciosamente valores omitidos; descartadas.
- **Consecuencias:** el request de creación y actualización requiere `ip_address` y `status`; ambos campos opcionales se serializan como strings, incluidos sus defaults.
- **Aprobación:** instrucción del usuario para cerrar los pendientes de IPAM.

### DEC-IPAM-04 — Límite de concurrencia y rechazo inmediato

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** limitar las operaciones IPAM concurrentes y definir el comportamiento al agotarse el límite.
- **Decisión:** la API usa `asyncio.Semaphore(5)` y, si no hay permiso disponible, responde inmediatamente HTTP 429 con código `too_many_requests`.
- **Motivo:** establecer un límite operativo y evitar una cola de solicitudes sin límite definido.
- **Alternativas:** esperar a que se libere un permiso; descartada.
- **Consecuencias:** el semáforo limita un proceso/event loop; el límite global entre múltiples workers permanece sin decisión.
- **Aprobación:** instrucción del usuario para cerrar los pendientes de IPAM.

## Decisiones pendientes

- Si el dominio normaliza la representación IPv4 antes de persistir/comparar.
- Si el semáforo de cinco operaciones debe limitar un solo proceso o el despliegue completo.
- Reconciliar el estado de la herramienta en el catálogo cuando se implemente e integre; el catálogo aún la marca pendiente.
