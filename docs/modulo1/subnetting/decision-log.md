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
- **Consecuencias:** la capacidad efectiva de un `/31` punto a punto es de dos direcciones de host. La API actual conserva `broadcast` como la dirección matemática de `IPv4Network.broadcast_address` y devuelve `first_host`/`last_host` nulos para bloques de dos direcciones; esa diferencia queda registrada como incompatibilidad entre la regla y la representación actual pendiente de reconciliación.

## Observación pendiente

El código calcula una capacidad de una dirección para `/32`, pero no hay en este registro una decisión adicional sobre cómo exponer los campos `broadcast`, `first_host` y `last_host` para `/32`. La implementación actual devuelve `first_host` y `last_host` como `null` para ese tamaño de bloque. No se eleva ese detalle de serialización a una regla aprobada.
