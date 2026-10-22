# Registro de decisiones — Traceroute

Este documento registra decisiones específicas de la herramienta 7. Las decisiones globales están en [`docs/fundacional/decision-log.md`](../../fundacional/decision-log.md); no se replican aquí como fuente normativa.

## Decisiones aprobadas

### TRACE-DEC-001 — Entrada y alcance de saltos

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** la herramienta debe diagnosticar la ruta de un destino sin permitir parámetros arbitrarios del sistema operativo.
- **Decisión:** aceptar `host` IPv4, IPv6 o dominio. El campo `max_hops` opcional y sus límites se detallan en DEC-TRACE-04.
- **Motivo:** instrucción explícita del usuario.
- **Alternativas:** no registradas.
- **Consecuencias:** el cliente no controla flags adicionales ni el ejecutable.
- **Aprobación:** solicitud de documentar la Herramienta 7, 2026-10-19.

### TRACE-DEC-002 — Dominio separado y runner inyectado

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** la lógica de interpretación debe probarse sin lanzar procesos ni depender directamente de Windows.
- **Decisión:** `netops_desk/traceroute.py` recibe un `TracerouteRunner` inyectado y no importa `subprocess`.
- **Motivo:** instrucción explícita del usuario y principio arquitectónico de separar dominio e integración de sistema operativo.
- **Alternativas:** no registradas.
- **Consecuencias:** API/adaptador ejecuta `tracert.exe`; el dominio se prueba con runner falso y fixtures.
- **Aprobación:** solicitud del usuario, 2026-10-19.

### TRACE-DEC-003 — Ejecución Windows y límites del proceso

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** `tracert.exe` puede consumir tiempo y producir salida extensa; el host procede de una solicitud externa.
- **Decisión:** invocar `tracert` con `["tracert", "/h", str(max_hops), "/w", "1000", "/d", host]`, usando argumentos separados y `shell=False`; timeout total duro de 30 segundos; no retener más de 64 KiB de stdout.
- **Motivo:** límites defensivos de proceso, tiempo y memoria indicados por el usuario.
- **Alternativas:** no registradas.
- **Consecuencias:** el deadline total puede interrumpir una ejecución antes de que termine el máximo de saltos. El método concreto para aplicar el límite de stdout durante la lectura y el error ante exceso requieren especificación de implementación. Se usan las barras documentadas por Microsoft Learn.
- **Aprobación:** solicitud del usuario, 2026-10-19.

### TRACE-DEC-004 — Interpretación de filas y saltos sin respuesta

- **Estado:** APROBADA en el alcance indicado
- **Fecha:** 2026-10-19
- **Contexto:** la salida de Windows contiene filas numeradas, tiempos y asteriscos para sondas que no recibieron respuesta.
- **Decisión:** parsear filas por número de salto al inicio; interpretar `*` como timeout de una sonda; si la fila no tiene IP y presenta timeouts, devolver `ip: null` y `times_ms: []`.
- **Motivo:** instrucción del usuario y formato descrito para el resultado.
- **Alternativas:** no registradas.
- **Consecuencias:** parsing de mensajes completos localizados no debe ser requisito para identificar el número, RTT o IP. DEC-TRACE-05 fija la representación de saltos sin respuesta y respuestas parciales.
- **Aprobación:** solicitud del usuario, 2026-10-19.

## Decisiones aprobadas adicionales

### DEC-TRACE-04 — Límite de saltos

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** la cantidad de saltos afecta la duración y el consumo de la operación.
- **Decisión:** `max_hops` es entero entre 1 y 30; si se omite, vale 15.
- **Motivo:** límite aprobado por el usuario para acotar la traza y preservar un default más breve que el máximo del ejecutable.
- **Alternativas:** no registradas.
- **Consecuencias:** entradas fuera de rango o no enteras se rechazan antes de ejecutar `tracert.exe`.
- **Aprobación:** instrucción explícita del usuario, 2026-10-19.

### DEC-TRACE-05 — Saltos perdidos y respuestas parciales

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** `tracert.exe` representa probes sin respuesta con `*`; una fila puede contener entre cero y tres tiempos.
- **Decisión:** conservar todos los saltos observados y ordenarlos por `hop_number`. Si no responde ningún probe del salto, usar `ip: null` y `times_ms: []`; si responden uno o dos, incluir solo los RTT numéricos recibidos, sin `null` de relleno.
- **Motivo:** no descartar saltos ni fabricar valores que la salida no proporciona.
- **Alternativas:** no registradas.
- **Consecuencias:** el array de tiempos parciales no conserva la posición de los probes perdidos.
- **Aprobación:** instrucción explícita del usuario, 2026-10-19.

### DEC-TRACE-06 — Errores HTTP y concurrencia global

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** separar un resultado de ruta completada de validación inválida, timeout del proceso, fallo local de ejecución y saturación de recursos.
- **Decisión:** HTTP 200 si la traza llega al destino o alcanza `max_hops`; 422 para host o `max_hops` inválidos (`invalid_host`, `invalid_max_hops`); 504 al superar 30 s (`traceroute_timeout`); 500 ante fallo de ejecución del binario (`execution_failed`); y 429 cuando se supera el límite de concurrencia (`too_many_requests`). Aplicar `asyncio.Semaphore(3)` global y desplegar con un solo worker.
- **Motivo:** diferenciar estado de red y fallos de entrada/proceso, limitando el coste simultáneo de una herramienta de mayor duración.
- **Alternativas:** no registradas.
- **Consecuencias:** no escalar a varios workers en esta versión; el status/código por exceso del límite stdout de 64 KiB queda pendiente.
- **Aprobación:** instrucción explícita del usuario, 2026-10-19.

## Propuestas y decisiones pendientes

### TRACE-PROP-001 — Formalización común para Módulo 2 y exceso de stdout

- **Estado:** PROPUESTA; aprobación pendiente
- **Fecha:** 2026-10-19
- **Contexto:** DEC-012 formaliza el sobre común de errores del Módulo 1; además, no se definió el status/código para superar 64 KiB de stdout.
- **Decisión propuesta:** formalizar el sobre JSON y los errores compartidos para Módulo 2; elegir el status/código de salida excesiva sin alterar los códigos ya aprobados en DEC-TRACE-06.
- **Motivo:** mantener contratos homogéneos sin extender decisiones de Módulo 1 por inferencia.
- **Alternativas:** conservar errores específicos en cada herramienta; no evaluadas.
- **Consecuencias:** afecta contratos de Ping/Traceroute y sus handlers, pero no cambia los status particulares ya aprobados para Traceroute.
- **Aprobación:** pendiente del usuario.

### TRACE-PROP-002 — Selección de familia y nombres DNS

- **Estado:** PROPUESTA; aprobación pendiente
- **Fecha:** 2026-10-19
- **Contexto:** el comando documentado no incluye `/4` ni `/6`, y la política DNS de Ping todavía tiene decisiones pendientes.
- **Decisión propuesta:** definir selección de familia para dominios y política IDN/FQDN; definir controles de frecuencia antes de exposición multiusuario. La concurrencia de Traceroute está aprobada en DEC-TRACE-06.
- **Motivo:** los flags de familia modifican el comportamiento; las reglas de Ping aún no cierran la admisión de nombres DNS.
- **Alternativas:** forzar familia para toda solicitud o dejar la selección al sistema; no se decide aquí.
- **Consecuencias:** afecta compatibilidad con dominios e integración de plataforma.
- **Aprobación:** pendiente del usuario.
