# Contrato de API — Planificador VLSM

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

## Errores observados

| Estado HTTP | Condición | Cuerpo observado |
|---|---|---|
| `422` | Entrada incompatible con las restricciones de Pydantic, como una lista vacía, `hosts <= 0` o un nombre vacío. | JSON de validación producido por el handler común. |
| `400` | El dominio rechaza una red no compatible o una asignación que excede la capacidad. | El router envuelve el detalle de `DomainError` en `HTTPException(400)`; el handler HTTP común asigna `error: "invalid_json"` a los estados 400. |

La asignación de `invalid_json` al estado 400 es la conducta actual compartida de la aplicación; no implica que el error de capacidad sea JSON inválido ni establece un código de error VLSM propio.
