# Contrato de API — Planificador VLSM

Las convenciones comunes de errores HTTP están en [`docs/modulo1/api-contracts.md`](../api-contracts.md). Este documento define la ruta, entrada y respuesta específicas del Planificador VLSM.

## Endpoint

`POST /api/v1/tools/vlsm/calculate`

La solicitud y la respuesta usan JSON. Los nombres y tipos descritos aquí corresponden a los modelos Pydantic actuales de `src/netops_desk/api/models/vlsm.py`.

## Solicitud

```json
{
  "network_cidr": "192.168.1.0/24",
  "requirements": [
    {"name": "Ventas", "hosts": 100},
    {"name": "IT", "hosts": 50}
  ]
}
```

| Campo | Tipo | Restricción del modelo |
|---|---|---|
| `network_cidr` | cadena | Obligatorio. El dominio interpreta la red CIDR y normaliza bits de host. |
| `requirements` | lista | Obligatoria y no vacía. |
| `requirements[].name` | cadena | Obligatorio, longitud mínima 1. |
| `requirements[].hosts` | entero | Obligatorio, mayor que 0. |

## Respuesta exitosa

HTTP `200`:

```json
{
  "base_network": "192.168.1.0/24",
  "allocated": [
    {
      "name": "Ventas",
      "network": "192.168.1.0",
      "prefix": 25,
      "netmask": "255.255.255.128",
      "broadcast": "192.168.1.127",
      "first_host": "192.168.1.1",
      "last_host": "192.168.1.126",
      "total_ips": 128,
      "hosts_needed": 100
    },
    {
      "name": "IT",
      "network": "192.168.1.128",
      "prefix": 26,
      "netmask": "255.255.255.192",
      "broadcast": "192.168.1.191",
      "first_host": "192.168.1.129",
      "last_host": "192.168.1.190",
      "total_ips": 64,
      "hosts_needed": 50
    }
  ],
  "remaining": [
    {
      "network": "192.168.1.192",
      "broadcast": "192.168.1.255",
      "total_ips": 64
    }
  ]
}
```

`allocated` se ordena por cantidad de hosts solicitada, de mayor a menor. `remaining` contiene el intervalo libre final cuando existe; si la asignación consume todo el espacio, es `[]`. `total_ips` expresa direcciones totales.

## Errores específicos y brecha de implementación

El contrato común establece HTTP `422` para entradas inválidas y errores de dominio, con el sobre `{ "error": "<código>", "detail": "<mensaje>" }`.

La implementación actual convierte `DomainError` en HTTP `400`; el handler global responde con el código `bad_request`. Esta diferencia queda pendiente de resolución en código y no modifica el contrato aprobado. Los errores de esquema de Pydantic permanecen en HTTP `422`.
