# Registro de decisiones — Visor de tabla de rutas

Este registro contiene las decisiones aprobadas para documentar la herramienta 14. Los detalles marcados como pendientes no son decisiones aprobadas.

## Decisiones

### RT-DEC-001 — Consulta IPv4 de solo lectura

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** la herramienta debe mostrar la tabla local de rutas sin recibir filtros del cliente.
- **Decisión:** exponer una consulta GET sin parámetros y usar el comando fijo `route print -4`.
- **Motivo:** limitar la operación a lectura de rutas IPv4 del servidor.
- **Alternativas:** recibir comandos o filtros del request; no adoptadas.
- **Consecuencias:** ninguna entrada HTTP se incorpora a los argumentos de proceso; la salida describe el servidor, no el equipo navegador.
- **Aprobación:** solicitud explícita del usuario para la herramienta 14.

### RT-DEC-002 — Dominio con runner inyectado y reutilización

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** Route Analyzer ya ejecuta y parsea `route print -4`; la herramienta 14 debe evitar duplicar lógica divergente.
- **Decisión:** el dominio `netops_desk/route_table.py` recibe un `RouteTableRunner`. Se reutilizará el adaptador de la herramienta 10 o su patrón de parsing; el dominio de Route Table no importará el dominio de Route Analyzer.
- **Motivo:** compartir comportamiento de plataforma y parsing preservando los límites entre dominios.
- **Alternativas:** duplicar el parser sin referencia a la herramienta 10; no adoptada como objetivo.
- **Consecuencias:** el parser debe conservar el reconocimiento estructural de cuatro tokens IPv4 más métrica. La forma concreta de compartir la implementación se decide al implementar.
- **Aprobación:** solicitud explícita del usuario para la herramienta 14.

### RT-DEC-003 — Ejecución, concurrencia y rutas On-link

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** la tabla puede ser extensa y contiene filas especiales sin gateway IPv4.
- **Decisión:** timeout de 10 segundos; `asyncio.Semaphore(5)` global; omitir filas `On-link` en la respuesta.
- **Motivo:** acotar duración/concurrencia y mantener el contrato `gateway` como IPv4.
- **Alternativas:** representar `gateway` como nulo para `On-link`; la opción elegida es omitir esas filas.
- **Consecuencias:** el límite global requiere un solo worker Uvicorn; la conducta ante saturación se especifica en RT-DEC-006. El límite de bytes de stdout queda pendiente.
- **Aprobación:** solicitud explícita del usuario para la herramienta 14.

### RT-DEC-004 — Errores del comando y respuesta vacía

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** una tabla válida puede no contener filas; un fallo o timeout impide completar la consulta.
- **Decisión:** ante fallo del comando o timeout, el dominio lanza `DomainError` con código `execution_failed`, que el handler global mapea a HTTP 422. Si la consulta se completa y no hay rutas, responder HTTP 200 con `routes: []`.
- **Motivo:** distinguir una consulta válida sin resultados de un fallo de ejecución y mantener la traducción común de `DomainError`.
- **Alternativas:** tratar tabla vacía como error; descartada.
- **Consecuencias:** el contrato conserva una respuesta vacía normal; otros errores de parseo requieren definición.
- **Aprobación:** resolución explícita del usuario en la tarea de cierre documental.

### RT-DEC-005 — Filas On-link y estructura de fila

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** `On-link` no es una dirección IPv4 y el campo `gateway` del contrato es string IPv4.
- **Decisión:** ignorar filas `On-link`; aceptar solo filas con cuatro direcciones IPv4 válidas (destino, máscara, gateway e interfaz) y una métrica entera final.
- **Motivo:** no fabricar gateways ni ampliar el esquema de respuesta.
- **Alternativas:** representar gateway nulo; descartada para esta versión.
- **Consecuencias:** las rutas on-link no aparecen en la respuesta aunque estén en la salida del sistema; las direcciones deben validarse, no solo reconocerse léxicamente.
- **Aprobación:** resolución explícita del usuario en la tarea de cierre documental.

### RT-DEC-006 — Rechazo por saturación del semáforo

- **Estado:** APROBADA.
- **Fecha:** 2026-10-20.
- **Contexto:** la herramienta está limitada a cinco consultas concurrentes.
- **Decisión:** si `asyncio.Semaphore(5)` no tiene permiso disponible, responder HTTP 429 con código `too_many_requests`.
- **Motivo:** evitar que las solicitudes excedentes esperen sin límite.
- **Alternativas:** esperar a que se libere un permiso; descartada.
- **Consecuencias:** garantizar el límite global requiere un único worker Uvicorn, porque el semáforo asyncio no coordina procesos.
- **Aprobación:** resolución explícita del usuario en la tarea de cierre documental.

## Pendientes; no son decisiones aprobadas

- Mapeo HTTP para salida no parseable que no provenga de fallo/timeout del comando.
- Máximo de bytes leídos de stdout, orden de rutas y conducta ante resultado parcial.
- Forma concreta de compartir el adaptador/parser con Route Analyzer sin ejecutar `ipconfig` innecesariamente.
