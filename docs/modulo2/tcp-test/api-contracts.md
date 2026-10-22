# Contrato de API — Prueba de puertos TCP

## Estado

Contrato objetivo de la herramienta 8; no hay endpoint TCP implementado en el repositorio. Los elementos indicados como pendientes no deben tratarse como decisiones aprobadas.

## Endpoint

`POST /api/v1/tools/tcp-test/execute`

## Solicitud

```json
{
  "host": "8.8.8.8",
  "port": 443,
  "timeout_ms": 3000
}
```

| Campo | Tipo | Requerido | Regla |
|---|---|---:|---|
| `host` | string | Sí | IPv4, IPv6 o dominio válido conforme a la política de validación de Ping. |
| `port` | integer | Sí | De 1 a 65535, inclusive. No aceptar booleanos como enteros. |
| `timeout_ms` | integer | No | Default 3000; mínimo 500 y máximo 10000, inclusive. |

No se especifican aquí campos adicionales. Si se adopta rechazo de campos desconocidos (`extra="forbid"`), debe registrarse como decisión antes de implementarlo.

## Respuesta de resultado

Resultado `open` de ejemplo:

```json
{
  "host": "8.8.8.8",
  "port": 443,
  "status": "open",
  "time_ms": 45.2
}
```

`status` puede ser:

| Valor | Significado |
|---|---|
| `open` | Se estableció la conexión TCP. |
| `closed` | El destino rechazó inmediatamente la conexión. |
| `filtered` | No se recibió respuesta antes del timeout de conexión. No prueba por sí solo que un firewall filtró el tráfico. |

Los tres estados (`open`, `closed` y `filtered`) son resultados válidos del diagnóstico y devuelven HTTP `200 OK`, incluso si el puerto está cerrado o no responde. `time_ms` es un número no negativo que incluye la resolución DNS y el handshake TCP, medidos durante la llamada completa a `socket.create_connection`.

## Errores HTTP

Los errores de validación y de disponibilidad de red usan el sobre común `{ "error": "<código>", "detail": "<mensaje>"}`. Los resultados de conexión (`open`, `closed`, `filtered`) no son errores HTTP.

| Estado | Situación | Estado de definición |
|---|---|---|
| `422` | Host, puerto o timeout inválido. DNS (`socket.gaierror`) o red inalcanzable (`OSError` distinto de rechazo y timeout). | `invalid_host`, `invalid_port`, `invalid_timeout` o `host_unreachable`. |
| `504` | Se excede el límite duro de 15 segundos del servidor. | `tcp_test_timeout`. |
| `500` | Falla inesperada no clasificada del runner o del sistema. | `execution_failed`. |
| `429` | Los 10 permisos del semáforo están ocupados; la solicitud se rechaza sin esperar. | `too_many_requests`. |

DNS y los errores de red inalcanzable no se presentan como `closed` o `filtered`: el dominio lanza `DomainError` con código `host_unreachable`, traducido a HTTP `422`. Los mensajes destinados al usuario deben estar en español. La aplicación de estas decisiones a la política transversal del Módulo 2 deberá mantenerse consistente con el contrato común.

## Decisiones relacionadas

- [Registro de decisiones TCP](decision-log.md).
- [Contrato común del Módulo 1](../../modulo1/api-contracts.md), referencia vigente en ese módulo.
- [Decisiones fundacionales](../../fundacional/decision-log.md), DEC-011 y DEC-012.
