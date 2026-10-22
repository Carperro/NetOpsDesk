# Contrato de API — Diagnóstico DNS

## Estado

Contrato objetivo de la herramienta 9; el catálogo la marca como pendiente de desarrollo e integración. Los estados de diagnóstico están especificados, pero el mapeo HTTP de sus errores permanece pendiente.

## Endpoint

`POST /api/v1/tools/dns-test/execute`

## Solicitud

```json
{
  "domain": "google.com",
  "record_type": "MX",
  "resolver": "8.8.8.8"
}
```

| Campo | Tipo | Requerido | Regla |
|---|---|---:|---|
| `domain` | string | Sí | Nombre de dominio válido; no URL. La política de IDN y punto final se debe fijar antes de implementar. |
| `record_type` | string | Sí | Uno de `A`, `AAAA`, `MX`, `TXT`, `NS`, `CNAME`. |
| `resolver` | string (IP) o `null` | No | IPv4 o IPv6 literal del nameserver. Si no se envía o vale `null`, se usa la configuración DNS del sistema. |

El comportamiento ante campos adicionales aún no está decidido. Rechazarlos con `extra="forbid"` es una propuesta que debe confirmarse al definir el modelo.

## Respuesta de diagnóstico

Ejemplo de respuesta positiva usando un resolver explícito:

```json
{
  "domain": "google.com",
  "record_type": "MX",
  "resolver": "8.8.8.8",
  "status": "success",
  "time_ms": 35.4,
  "records": [
    "10 smtp.google.com"
  ]
}
```

Campos:

| Campo | Tipo | Significado |
|---|---|---|
| `domain` | string | Nombre consultado. |
| `record_type` | string | Tipo de registro consultado. |
| `resolver` | string o null | Resolver solicitado; la representación cuando se usa DNS del sistema requiere decisión. |
| `status` | string | Estado de diagnóstico: `success`, `nxdomain` o `error`. |
| `time_ms` | number | Duración total de la consulta, limitada a 5000 ms. |
| `records` | array de strings | Registros convertidos a texto; vacío cuando no hay registros que devolver. |

Para MX, cada elemento usa prioridad seguida del servidor. El formato textual para TXT y la normalización de nombres con punto final deben fijarse para que el contrato sea estable.

Si la solicitud omite `resolver` o lo envía como `null`, la respuesta incluye `"resolver": "system"` para indicar que se usó el DNS configurado en Windows.

Ejemplo de respuesta cuando el DNS confirma NXDOMAIN:

```json
{
  "domain": "dominio-inexistente.example",
  "record_type": "A",
  "resolver": "system",
  "status": "nxdomain",
  "time_ms": 18.2,
  "records": []
}
```

## Estados de diagnóstico y HTTP

| Estado del resultado | Significado | Mapeo HTTP |
|---|---|---|
| `success` | La consulta obtuvo registros. | `200` para respuesta positiva. |
| `nxdomain` | El resolver respondió que el nombre consultado no existe. | `200 OK`; es una respuesta válida del servidor DNS y `records` es `[]`. |
| `error` | SERVFAIL, ausencia de respuesta u otra falla de consulta. | Pendiente, salvo timeout DNS descrito abajo. |

Si dnspython produce `dns.exception.Timeout`, la API responde HTTP `504 Gateway Timeout` con el código `dns_timeout`. El mapeo de otros errores DNS, validación, tipo de contenido y saturación del semáforo queda pendiente de formalizar en el contrato transversal del Módulo 2. No inferir códigos públicos a partir de DEC-012, que gobierna el Módulo 1.

## Referencias

- [Requisitos](requisitos.md).
- [Arquitectura](arquitectura.md).
- [Registro de decisiones](decision-log.md).
- [Contrato común del Módulo 1](../../modulo1/api-contracts.md), solo como referencia existente.
