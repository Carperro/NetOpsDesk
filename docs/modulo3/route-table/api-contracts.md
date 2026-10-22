# Contrato de API — Visor de tabla de rutas

> Contrato objetivo basado en la solicitud del usuario. No se verificó una implementación específica de esta herramienta.

## Operación: consultar tabla de rutas IPv4

- **Método y ruta:** `GET /api/v1/tools/route-table/execute`
- **Propósito:** devolver las rutas IPv4 locales que el parser reconoce en el equipo servidor.
- **Content-Type:** no aplica a la solicitud sin body; la respuesta es JSON.

### Solicitud

No se envían parámetros, query string ni cuerpo.

### Respuesta correcta

- **Estado:** HTTP `200 OK` cuando el comando y el parseo completan correctamente.
- **Esquema:** objeto con `routes`, una lista de rutas IPv4.

Una consulta correcta sin rutas devuelve:

```json
{ "routes": [] }
```

Una respuesta con rutas puede tener esta forma:

```json
{
  "routes": [
    {
      "destination": "0.0.0.0",
      "netmask": "0.0.0.0",
      "gateway": "192.168.1.1",
      "interface": "192.168.1.33",
      "metric": 35
    }
  ]
}
```

| Campo | Tipo | Semántica |
|---|---|---|
| `routes` | array | Rutas IPv4 reconocidas; no contiene filas `On-link` |
| `routes[].destination` | string IPv4 | Destino de red de la ruta |
| `routes[].netmask` | string IPv4 | Máscara de red |
| `routes[].gateway` | string IPv4 | Gateway de la ruta |
| `routes[].interface` | string IPv4 | Dirección IPv4 de la interfaz asociada |
| `routes[].metric` | integer | Métrica numérica de la ruta |

El parser solo acepta filas con cuatro direcciones IPv4 válidas (destino, máscara, gateway e interfaz) y una métrica entera final. Las filas `On-link` se ignoran y no se incluyen en `routes`. Si el comando termina correctamente pero no hay filas aceptadas, la respuesta es `200 OK` con `routes: []`.

### Errores

Si el comando falla o supera el timeout, el dominio lanza `DomainError` con código `execution_failed`; el handler global lo mapea a HTTP `422`. Si no hay permiso disponible en el semáforo de cinco operaciones, la API responde HTTP `429` con código `too_many_requests`. No se presume automáticamente la extensión de DEC-012 del Módulo 1 para otros errores.

| HTTP | Código `error` | Cuándo ocurre | Estado |
|---|---|---|---|
| `422` | `execution_failed` | El comando falla o supera el timeout de 10 segundos; `DomainError` se traduce por el handler global | Aprobado |
| `429` | `too_many_requests` | Se agotaron los cinco permisos globales del semáforo | Aprobado |

## Compatibilidad y verificación

- **OpenAPI:** endpoint objetivo GET sin body; no se inspeccionó implementación específica.
- **Pruebas de contrato:** pendientes de crear junto con la implementación.
- **Cambios incompatibles o pendientes:** mapeo de salidas no parseables y orden de rutas.
