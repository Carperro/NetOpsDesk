# Registro de decisiones — Prueba de puertos TCP

## Estado

Este registro distingue las decisiones expresamente indicadas para documentar la herramienta de las cuestiones que siguen abiertas. Fecha de registro: 2026-10-20. No implica que la implementación exista.

## Decisiones aprobadas para la especificación

### TCP-DEC-001 — Entrada y alcance de la prueba

- **Estado:** APROBADA por instrucción del usuario.
- **Decisión:** La operación recibe host IPv4, IPv6 o dominio, un puerto TCP de 1 a 65535 y un `timeout_ms` opcional entre 500 y 10000 ms, con default 3000 ms.
- **Consecuencia:** La herramienta prueba una sola combinación de host y puerto; no realiza barridos.

### TCP-DEC-002 — Endpoint y resultado

- **Estado:** APROBADA por instrucción del usuario.
- **Decisión:** El endpoint objetivo es `POST /api/v1/tools/tcp-test/execute`. El resultado contiene `host`, `port`, `status` y `time_ms`; los estados previstos son `open`, `closed` y `filtered`.

### TCP-DEC-003 — Dominio independiente con runner inyectado

- **Estado:** APROBADA por instrucción del usuario.
- **Decisión:** El dominio previsto en `netops_desk/tcp_test.py` recibe un `TcpRunner` inyectado y no importa `socket`. El runner de infraestructura usa `socket.create_connection((host, port), timeout)`.

### TCP-DEC-004 — Interpretación de resultados del socket

- **Estado:** APROBADA por instrucción del usuario.
- **Decisión:** Conexión establecida → `open`; `ConnectionRefusedError` inmediato → `closed`; `TimeoutError` o `socket.timeout` → `filtered`.
- **Consecuencia:** `filtered` describe ausencia de respuesta dentro del plazo; no atribuye causalidad a un firewall.

### TCP-DEC-005 — Concurrencia y límite de ejecución

- **Estado:** APROBADA por instrucción del usuario.
- **Decisión:** La API aplicará `asyncio.Semaphore(10)` con rechazo inmediato `429 Too Many Requests` cuando los diez permisos estén ocupados. Cada ejecución tendrá un límite duro de servidor de 15 segundos.
- **Consecuencia:** El semáforo solo limita globalmente las solicitudes con un worker. La condición de despliegue de un solo worker y el mecanismo del límite exterior deben verificarse al implementar.

### TCP-DEC-006 — Resultados de diagnóstico HTTP 200

- **Estado:** APROBADA por instrucción del usuario.
- **Decisión:** `open`, `closed` y `filtered` se devuelven con HTTP `200 OK`; son resultados de diagnóstico, no errores de API.

### TCP-DEC-007 — Errores DNS y de red inalcanzable

- **Estado:** APROBADA por instrucción del usuario.
- **Decisión:** `socket.gaierror` y `OSError` distintos de timeout o rechazo se convierten en `DomainError` con código `host_unreachable`, que se traduce a HTTP `422`.
- **Consecuencia:** Los errores de infraestructura no se confunden con `closed` o `filtered`.

### TCP-DEC-008 — Medición de `time_ms`

- **Estado:** APROBADA por instrucción del usuario.
- **Decisión:** `time_ms` incluye el tiempo de resolución DNS y el handshake TCP, es decir, el tiempo total de la llamada a `socket.create_connection`.

## Pendientes de decisión

### TCP-PEND-001 — Validación de dominios

La instrucción remite al regex/política de Ping. La política común de IDN y otros casos de nombres debe confirmarse en su documentación antes de reutilizarla literalmente.

### TCP-PEND-002 — Sobre y códigos transversales del Módulo 2

DEC-012 documenta la semántica común del Módulo 1. Su aplicación a herramientas del Módulo 2, incluidos códigos y mensajes en español, requiere confirmación o una decisión transversal nueva.
