# Registro de decisiones — Subnetting IPv4

Este registro contiene decisiones autorizadas para Subnetting IPv4. El alcance de su inclusión en el MVP está en `docs/modulo1/ipv4-calculator/decision-log.md` (DEC-009).

## Decisiones aprobadas

### SUB-DEC-001 — Uso de `ipaddress`

- **Estado:** APROBADA.
- **Contexto:** cálculo de redes y subredes IPv4.
- **Decisión:** utilizar la biblioteca estándar de Python `ipaddress` para representar y dividir redes CIDR.
- **Motivo:** decisión técnica expresamente aprobada para la implementación de esta herramienta; no se registra una justificación histórica adicional.
- **Consecuencias:** el dominio utiliza la biblioteca estándar y no requiere una dependencia externa para las operaciones CIDR.

### SUB-DEC-002 — Capacidad de enlaces IPv4 `/31`

- **Estado:** APROBADA.
- **Contexto:** enlaces punto a punto con prefijo `/31`.
- **Decisión:** aplicar la regla de [RFC 3021, sección 2.1](https://www.rfc-editor.org/rfc/rfc3021.html#section-2.1): en un enlace punto a punto, las dos direcciones del bloque `/31` se interpretan como direcciones de host. No se reserva una dirección para broadcast dirigido en ese enlace.
- **Motivo:** RFC 3021 especifica la interpretación de las dos direcciones para este uso punto a punto.
- **Consecuencias:** la capacidad efectiva de un `/31` punto a punto es de dos direcciones de host. La API conserva `broadcast` como la dirección matemática de `IPv4Network.broadcast_address` y devuelve `first_host`/`last_host` nulos para bloques de dos direcciones o menos. Esta diferencia entre la semántica conceptual de RFC 3021 y la representación serializada vigente se mantiene conscientemente por compatibilidad con el contrato público actual; no se considera un bug de implementación.

### SUB-DEC-003 — Límite de subredes generadas

- **Estado:** APROBADA.
- **Contexto:** las operaciones de Subnetting materializan listas de subredes en memoria.
- **Decisión:** limitar a 4096 la cantidad de subredes generadas por solicitud, tanto al solicitar una cantidad explícita como al calcular por cantidad de hosts.
- **Motivo:** acotar el consumo de memoria y el tamaño de la respuesta.
- **Consecuencias:** solicitudes cuya cantidad solicitada o generada supere 4096 se rechazan con HTTP 422 y `insufficient_capacity`.

## Observación pendiente

El código calcula una capacidad de una dirección para `/32`, pero no hay en este registro una decisión adicional sobre cómo exponer los campos `broadcast`, `first_host` y `last_host` para `/32`. La implementación actual devuelve `first_host` y `last_host` como `null` para ese tamaño de bloque. No se eleva ese detalle de serialización a una regla aprobada.
