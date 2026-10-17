# Contratos de API — Subnetting IPv4

## Alcance

Este documento describe las rutas y modelos presentes en `src/netops_desk/api/routes/subnetting.py` y `src/netops_desk/api/models/subnetting.py`. Las observaciones identificadas como comportamiento actual no implican que la respuesta sea una decisión estable cuando el código tiene una inconsistencia documentada.

## Entradas

Las dos operaciones usan `POST` y reciben JSON.

### Calcular por cantidad

`POST /api/v1/tools/subnetting/by-count`

```json
{
  "network_cidr": "192.168.1.0/24",
  "subnet_count": 2
}
```

| Campo | Tipo del modelo | Restricción |
|---|---|---|
| `network_cidr` | cadena | Obligatorio; debe poder interpretarse como red CIDR por el dominio. |
| `subnet_count` | entero | Obligatorio y mayor que cero. |

El dominio calcula `ceil(log2(subnet_count))` bits de división y devuelve exactamente la cantidad solicitada de las subredes de tamaño uniforme resultantes.

### Calcular por hosts

`POST /api/v1/tools/subnetting/by-hosts`

```json
{
  "network_cidr": "192.168.1.0/30",
  "required_hosts": 2
}
```

| Campo | Tipo del modelo | Restricción |
|---|---|---|
| `network_cidr` | cadena | Obligatorio; debe poder interpretarse como red CIDR por el dominio. |
| `required_hosts` | entero | Obligatorio y mayor que cero. |

El dominio calcula un prefijo de subred según la capacidad de hosts y devuelve las subredes que caben en la red base. Los casos `/31` y `/32` tienen las discrepancias descritas en `requisitos.md`; no se debe inferir de ellos una respuesta de rango que el serializador no entrega.

**Campos adicionales:** los modelos no configuran `extra="forbid"`; con la configuración predeterminada de Pydantic, los campos no declarados se ignoran. Esto describe el comportamiento actual.

## Respuesta exitosa

Ambos endpoints responden `200` con el modelo `SubnettingOutput`:

| Campo | Tipo | Presencia y significado actual |
|---|---|---|
| `subnets` | lista de `SubnetResult` | Siempre presente. |
| `was_normalized` | booleano | Siempre presente; indica si se normalizaron bits de host. |
| `original_network` | cadena | Siempre presente; contiene el CIDR normalizado, no la cadena de entrada original. |
| `new_prefix` | entero o `null` | Campo del modelo; se completa en el modo por hosts y vale `null` en el modo por cantidad. |
| `usable_hosts_per_subnet` | entero o `null` | Campo del modelo; se completa en el modo por hosts y vale `null` en el modo por cantidad. |

Cada elemento de `subnets` tiene este esquema:

| Campo | Tipo |
|---|---|
| `network` | cadena |
| `broadcast` | cadena |
| `prefixlen` | entero |
| `netmask` | cadena |
| `first_host` | cadena o `null` |
| `last_host` | cadena o `null` |
| `total_addresses` | entero |

El formateador calcula `broadcast` a partir de `IPv4Network.broadcast_address`. `first_host` y `last_host` se asignan solo si `total_addresses > 2`; para bloques de dos direcciones o menos ambos son `null`. Para el uso punto a punto de `/31`, esa representación no refleja por separado la semántica de RFC 3021; véase `requisitos.md`.

## Errores observados

Los handlers compartidos producen un objeto con `error` y `detail`.

| Estado | Comportamiento actual |
|---|---|
| `422` `missing_field` | Falta un campo obligatorio del modelo. |
| `422` `invalid_type` | Un valor no tiene el tipo requerido por el modelo. |
| `422` `invalid_value` | Un entero incumple `gt=0`, u otro valor Pydantic se clasifica como inválido. |
| `400` `invalid_json` | Las rutas convierten `ValueError` del dominio en HTTP 400; el handler común asigna `invalid_json`, incluso cuando el detalle corresponde a CIDR inválido o capacidad insuficiente. Esta asignación es una inconsistencia conocida, no una clasificación semántica aprobada para Subnetting. |
| `500` `internal_error` | Excepción inesperada; el handler común responde con un detalle genérico. |

No se define aquí un contrato de error más específico para Subnetting porque no existe una decisión de códigos propia del módulo y la traducción actual de HTTP 400 es genérica.
