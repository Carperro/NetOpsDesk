# Registro de decisiones — Visor de caché ARP

Este registro contiene las decisiones específicas aprobadas por el usuario para documentar la herramienta 13. Los puntos identificados como pendientes no son decisiones aprobadas.

## Decisiones

### ARP-DEC-001 — Consulta de caché ARP local

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** se necesita mostrar asociaciones IP/MAC observadas por la caché ARP del equipo local.
- **Decisión:** ofrecer una consulta GET sin parámetros que lea la tabla local de Windows mediante el comando fijo `arp -a`.
- **Motivo:** no hay destino aportado por el cliente; la herramienta inspecciona la caché existente.
- **Alternativas:** no registradas.
- **Consecuencias:** no se construyen argumentos desde input del cliente; la operación es de lectura y no actualiza la caché.
- **Aprobación:** solicitud explícita del usuario para la herramienta 13.

### ARP-DEC-002 — Separación entre dominio y runner

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** la ejecución de procesos depende del sistema operativo y no debe acoplarse a la lógica de parseo.
- **Decisión:** `netops_desk/arp_viewer.py` recibe un `ArpRunner` inyectado; el runner ejecuta `arp -a` con `shell=False` y devuelve bytes. El dominio decodifica con `errors="replace"` y parsea la salida.
- **Motivo:** permitir pruebas del parser sin lanzar procesos reales y mantener la dependencia de plataforma en infraestructura.
- **Alternativas:** ejecutar subprocess desde el dominio; no adoptada.
- **Consecuencias:** el runner debe aplicar timeout de 10 segundos; fallo de comando y timeout se traducen mediante `DomainError(code="execution_failed")` a HTTP 422 por el handler global.
- **Aprobación:** solicitud explícita del usuario para la herramienta 13.

### ARP-DEC-003 — Campos de respuesta y concurrencia

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** la respuesta debe describir cada asociación en la caché y limitar operaciones simultáneas.
- **Decisión:** cada entrada contiene `interface_ip`, `ip_address`, `mac_address` y `entry_type`; la API usa `asyncio.Semaphore(5)`.
- **Motivo:** exponer las propiedades necesarias para identificar la asociación y acotar concurrencia.
- **Alternativas:** no registradas.
- **Consecuencias:** el parser agrupa por interfaz. Para que el semáforo sea global entre solicitudes, el despliegue debe usar un solo worker Uvicorn; al agotarse se rechaza con HTTP 429 `too_many_requests`.
- **Aprobación:** solicitud explícita del usuario para la herramienta 13.

### ARP-DEC-004 — Fallos de ejecución y caché vacía

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** un fallo al ejecutar el comando o un timeout es un error del sistema; una caché vacía es un resultado válido.
- **Decisión:** ante fallo del comando o timeout, el dominio lanza `DomainError` con código `execution_failed`, que el handler global mapea a HTTP 422. Si el comando termina correctamente y no hay entradas, responder HTTP 200 con `entries: []`.
- **Motivo:** distinguir una consulta correcta sin resultados de la imposibilidad de completar la consulta, conservando el manejo de errores global acordado.
- **Alternativas:** no registradas.
- **Consecuencias:** el contrato distingue respuesta vacía exitosa de fallo de ejecución. La salida no parseable no queda clasificada por esta decisión.
- **Aprobación:** resolución explícita del usuario en la tarea de cierre documental.

### ARP-DEC-005 — Límite de entradas devueltas

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** una caché grande no debe producir un resultado de parseo ilimitado.
- **Decisión:** el parser devuelve como máximo 500 entradas.
- **Motivo:** limitar el trabajo y el tamaño del resultado expuesto por la herramienta.
- **Alternativas:** no registradas.
- **Consecuencias:** falta definir cuál subconjunto y orden se conservan si hay más de 500; el límite de bytes leídos de stdout también queda pendiente.
- **Aprobación:** resolución explícita del usuario en la tarea de cierre documental.

### ARP-DEC-006 — Semáforo global y rechazo por saturación

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** la lectura de proceso debe limitar operaciones simultáneas.
- **Decisión:** usar `asyncio.Semaphore(5)` global y rechazar solicitudes sin permiso con HTTP 429 `too_many_requests`.
- **Motivo:** acotar concurrencia sin dejar solicitudes excedentes en espera.
- **Alternativas:** espera en cola; no adoptada.
- **Consecuencias:** un `asyncio.Semaphore` no coordina varios procesos; garantizar el límite global requiere desplegar un solo worker Uvicorn.
- **Aprobación:** resolución explícita del usuario en la tarea de cierre documental.

### ARP-DEC-007 — Normalización de MAC y tipo de entrada

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** la salida de Windows puede variar en separadores y localización.
- **Decisión:** convertir MAC a minúsculas y reemplazar `:` por `-`; mapear `dinámica`/`dynamic` a `dynamic` y `estática`/`static` a `static`.
- **Motivo:** mantener un esquema estable para clientes independientemente de esas variaciones.
- **Alternativas:** no registradas.
- **Consecuencias:** el parser debe reconocer esas cuatro etiquetas y normalizar el formato antes de emitir la respuesta.
- **Aprobación:** resolución explícita del usuario en la tarea de cierre documental.

## Pendientes; no son decisiones aprobadas

- Estado HTTP para una salida que no puede parsearse.
- Límite de bytes leídos de stdout y selección/orden al superar 500 entradas.
- Requisito operativo de un único worker para sostener el límite global del semáforo.
- Variantes de idioma de encabezados y tipos fuera de `dinámica`/`dynamic` y `estática`/`static`.
