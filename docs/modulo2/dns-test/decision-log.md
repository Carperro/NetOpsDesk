# Registro de decisiones — Diagnóstico DNS

## Estado

Registro de las decisiones expresas y de las cuestiones todavía abiertas para la herramienta 9. La existencia de este documento no significa que la herramienta esté implementada.

## Decisiones aprobadas

### DEC-016 — Aprobación de `dnspython` para Diagnóstico DNS

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Alcance:** Herramienta 9, Diagnóstico DNS.
- **Contexto:** La librería estándar `socket` resuelve direcciones mediante la configuración del sistema, pero no proporciona la interfaz requerida para consultar tipos específicos como MX, TXT, NS y CNAME ni seleccionar un nameserver para comparar resolvers.
- **Decisión:** Aprobar `dnspython` como dependencia de la Herramienta 9. El adaptador `DnsRunner` usará `dns.resolver.Resolver` para consultas DNS y selección de nameserver.
- **Motivo:** La funcionalidad requerida excede las capacidades de consulta que se han elegido para `socket`; `dnspython` permite consultar los tipos definidos y dirigir las solicitudes a un resolver especificado.
- **Consecuencias:** La dependencia se incorporará al proyecto cuando se autorice la implementación y se actualizarán declaración y lockfile según DEC-015. El dominio no importará dnspython: la dependencia queda encapsulada en infraestructura.
- **Aprobación:** Instrucción explícita del usuario para documentar la Herramienta 9, 2026-10-20.

### DNS-DEC-001 — Entradas y tipos de registro

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Decisión:** Aceptar `domain`, `record_type` limitado a A, AAAA, MX, TXT, NS o CNAME, y `resolver` opcional como IP de nameserver. Si no se indica resolver, usar la configuración DNS del sistema.

### DNS-DEC-002 — Dominio separado de la consulta DNS

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Decisión:** El dominio previsto en `netops_desk/dns_test.py` recibe un `DnsRunner` inyectado y no importa dnspython. El runner usa `dns.resolver.Resolver`, efectúa la consulta síncrona y devuelve datos estructurados.

### DNS-DEC-003 — Endpoint y forma general de respuesta

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Decisión:** El endpoint objetivo es `POST /api/v1/tools/dns-test/execute`. La respuesta positiva incluye `domain`, `record_type`, `resolver`, `status`, `time_ms` y `records`; los estados de diagnóstico son `success`, `nxdomain` y `error`.

### DNS-DEC-004 — Límite de consulta y concurrencia

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Decisión:** Aplicar timeout duro de 5 segundos por consulta y usar `asyncio.Semaphore(10)` global en la capa API, desplegando un único worker de Uvicorn.
- **Consecuencia:** La operación síncrona debe ejecutarse de forma que no bloquee el event loop. No escalar a varios workers en este despliegue, porque cada proceso tendría un semáforo independiente. La conducta ante saturación sigue pendiente.

### DNS-DEC-005 — NXDOMAIN como resultado HTTP exitoso

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Decisión:** Si el dominio no existe, responder HTTP `200 OK` con `status: "nxdomain"` y `records: []`.
- **Motivo:** NXDOMAIN es una respuesta válida del servidor DNS y un resultado de diagnóstico, no un fallo HTTP.

### DNS-DEC-006 — Resolver del sistema en la respuesta

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Decisión:** Si el request omite `resolver` o lo envía como `null`, la API usa la configuración DNS de Windows y devuelve `resolver: "system"`.

### DNS-DEC-007 — Timeout DNS traducido a Gateway Timeout

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Decisión:** Si dnspython produce `dns.exception.Timeout`, la API responde HTTP `504 Gateway Timeout` con código `dns_timeout`.
- **Consecuencia:** El adaptador de infraestructura conserva el timeout como señal tipada para la capa API. El dominio no importa dnspython ni asigna estados HTTP.

## Propuestas y pendientes de decisión

### DNS-PEND-001 — Política exacta de nombres

Definir admisión de IDN, nombre absoluto con punto final, mayúsculas/minúsculas y reglas de etiquetas. Está confirmado que no se admiten URLs; los demás detalles no están fijados.

### DNS-PEND-003 — Serialización de registros TXT y nombres

Definir la representación textual interoperable de TXT (incluidos segmentos de cadena) y si los nombres de destino conservan el punto final absoluto.

### DNS-PEND-004 — Traducción HTTP de errores DNS distintos de NXDOMAIN y timeout

Definir el status y código público para SERVFAIL, ausencia de respuesta y error local. NXDOMAIN y `dns.exception.Timeout` ya se resuelven en DNS-DEC-005 y DNS-DEC-007.

### DNS-PEND-005 — Saturación del semáforo

Definir si las solicitudes concurrentes adicionales esperan o reciben HTTP 429. El límite global se cubre con un único worker según DNS-DEC-004.

### DNS-PEND-006 — Cuerpo de solicitud y campos desconocidos

Definir si el modelo rechaza campos adicionales (`extra="forbid"`) y los códigos HTTP detallados de validación conforme al contrato común del Módulo 2.
