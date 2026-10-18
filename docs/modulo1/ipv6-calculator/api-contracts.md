# Contrato de API — Calculadora IPv6

## Alcance

Este contrato define la versión inicial de la herramienta 5. Las reglas transversales de errores HTTP están en [`../api-contracts.md`](../api-contracts.md). La API v1 recibe exclusivamente `cidr`; no ofrece `address` + `netmask` ni cálculo inverso.

## Endpoint

- **Método:** `POST`.
- **Ruta:** `/api/v1/tools/ipv6/calculate`.
- **Router:** sin `prefix`; declara la ruta completa, como la calculadora IPv4.
- **Content-Type:** `application/json`.

## Solicitud

```json
{
  "cidr": "2001:db8::/64"
}
```

| Campo | Tipo | Restricción |
|---|---|---|
| `cidr` | cadena | Obligatorio. Dirección IPv6 con prefijo `/0` a `/128`. Puede ser una forma IPv6 válida con dirección IPv4 embebida/mapeada. No puede contener zone ID. |

El modelo Pydantic usa `extra="forbid"`: los campos desconocidos se rechazan con HTTP `422` y código `unknown_field`. El tipo JSON distinto de cadena se rechaza como error de validación; no se coerciona a texto.

## Respuesta exitosa — HTTP 200

```json
{
  "input": "2001:db8::/64",
  "address": "2001:db8::",
  "prefix_length": 64,
  "network": "2001:db8::",
  "last_address": "2001:db8::ffff:ffff:ffff:ffff",
  "total_addresses": "18446744073709551616",
  "host_bits_set": false,
  "classifications": [
    {
      "code": "documentation",
      "name": "Documentation",
      "prefix": "2001:db8::/32"
    }
  ],
  "warnings": []
}
```

### Ejemplo `/0` sin clasificación

```json
{
  "input": "::/0",
  "address": "::",
  "prefix_length": 0,
  "network": "::",
  "last_address": "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",
  "total_addresses": "340282366920938463463374607431768211456",
  "host_bits_set": false,
  "classifications": [],
  "warnings": []
}
```

### Ejemplo con bits de host activos

```json
{
  "input": "2001:db8::1/64",
  "address": "2001:db8::1",
  "prefix_length": 64,
  "network": "2001:db8::",
  "last_address": "2001:db8::ffff:ffff:ffff:ffff",
  "total_addresses": "18446744073709551616",
  "host_bits_set": true,
  "classifications": [
    {
      "code": "documentation",
      "name": "Documentation",
      "prefix": "2001:db8::/32"
    }
  ],
  "warnings": [
    {
      "code": "host_bits_normalized",
      "message": "La dirección contenía bits de host; se calculó la dirección de red."
    }
  ]
}
```

| Campo | Tipo | Semántica |
|---|---|---|
| `input` | cadena | Texto CIDR recibido, sin alteración. |
| `address` | cadena IPv6 | Dirección de entrada en representación canónica; conserva la parte de host antes de la normalización del prefijo. Una dirección IPv4 embebida/mapeada permanece representada como IPv6. |
| `prefix_length` | entero | Longitud validada, entre 0 y 128 inclusive. |
| `network` | cadena IPv6 | Dirección de red calculada con los bits de host en cero. |
| `last_address` | cadena IPv6 | Última dirección del bloque; no se denomina `broadcast`. |
| `total_addresses` | cadena decimal | Cantidad matemática exacta `2^(128-prefix_length)`. No debe serializarse como número JSON ni convertirse a JavaScript `Number`. |
| `host_bits_set` | booleano | `true` si la dirección de entrada tenía bits fuera del prefijo; `false` en otro caso. |
| `classifications` | lista de objetos | Entradas curadas aplicables a la dirección. Cada elemento usa `{code, name, prefix}`. Puede ser una lista vacía. El vocabulario y los rangos se mantienen como datos versionados vinculados a las fuentes IANA. |
| `warnings` | lista de objetos `{code, message}` | Siempre presente; vacía si no se normalizaron bits de host. Los mensajes dirigidos a personas están en español. |

La representación de las direcciones de respuesta será canónica conforme a RFC 5952. La clasificación se aplica a la dirección recibida, no pretende clasificar todas las direcciones del prefijo.

### Precisión de `total_addresses`

El total IPv6 puede alcanzar `2^128 = 340282366920938463463374607431768211456`, valor superior a `Number.MAX_SAFE_INTEGER` de JavaScript. Por eso el campo es una cadena decimal para preservar cada dígito entre el dominio, JSON y la interfaz. Es una divergencia deliberada del contrato IPv4, donde los totales caben en su representación actual; no se cambiará IPv4 como parte de este contrato.

## Advertencias

Si hay bits de host activos, se normaliza la dirección para el cálculo y la respuesta incluye:

```json
{
  "code": "host_bits_normalized",
  "message": "La dirección contenía bits de host; se calculó la dirección de red."
}
```

`address` conserva el valor de dirección recibido en forma canónica; `network` y `last_address` describen el bloque normalizado. No se rechaza la entrada únicamente por contener bits de host activos.

## Errores

Todas las respuestas de error usan el sobre `{ "error": string, "detail": string }`. Los errores de dominio se traducen por `domain_error_handler`; la ruta no implementa un mapeo propio.

El sobre `{error, detail}` y los estados HTTP se rigen por DEC-012 y el [contrato común del Módulo 1](../api-contracts.md).

| HTTP | Código | Condición |
|---|---|---|
| 400 | `invalid_json` | Error HTTP al leer/decodificar el cuerpo JSON, según el contrato común y DEC-007. |
| 404 | `not_found` | Ruta inexistente, con handler común. |
| 405 | `method_not_allowed` | Método no admitido, con handler común. |
| 415 | `unsupported_media_type` | El Content-Type no es `application/json`. |
| 422 | `invalid_json` | Error de sintaxis JSON que llega al validador Pydantic, según el contrato común y DEC-007. |
| 422 | `invalid_type`, `missing_field`, `unknown_field` u otro código común | El cuerpo no cumple el esquema de entrada. |
| 422 | `invalid_cidr` | Falta el separador CIDR o la parte de dirección no es IPv6 válida. `DomainError`. |
| 422 | `invalid_prefix` | El sufijo del prefijo no es entero o no está entre 0 y 128. `DomainError`. |
| 422 | `zone_id_not_supported` | La dirección contiene un zone ID (`%...`). `DomainError`. |
| 500 | `internal_error` | Error inesperado; detalle público genérico y seguro. |

Para los tres errores de dominio, la respuesta conserva `exc.code` en `error` y `exc.message` en `detail`; el handler establece HTTP 422. Los mensajes específicos deben estar en español.

## Clasificación IANA

La clasificación se sirve desde una tabla local curada, con fecha/versión y referencia de los prefijos. La tabla debe contrastarse con [IANA IPv6 Address Space](https://www.iana.org/assignments/ipv6-address-space), el [IANA IPv6 Special-Purpose Address Registry](https://www.iana.org/assignments/iana-ipv6-special-registry) y los registros IANA pertinentes para multicast/anycast. Cada coincidencia identifica `code`, nombre registral y `prefix`.

Las etiquetas describen entradas de registro. IANA advierte que pertenecer a un prefijo especial no garantiza su enrutabilidad en un contexto local o global. La respuesta no afirmará alcanzabilidad, anuncio ni condición simplificada «pública»/«privada». La muestra anterior usa el prefijo de documentación `2001:db8::/32`; la lista real debe incorporar la versión curada vigente cuando se implemente.
