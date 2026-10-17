# Contrato de API - Calculadora IPv4/CIDR (MVP)

Este documento describe el contrato que implementan actualmente `models.py`, `routes/ipv4.py`, `exceptions.py` y el dominio. Los códigos y mensajes se han contrastado con el código fuente; la presencia de pruebas asociadas no significa que se hayan ejecutado en esta actualización.

## Endpoint

- Método: `POST`.
- Ruta: `/api/v1/tools/ipv4/calculate`.
- `Content-Type`: se exige `application/json`; se permite el parámetro de charset porque la ruta compara el tipo MIME normalizado antes del punto y coma.

## Solicitudes

El modelo de entrada de API es `IPV4Input`. Rechaza campos adicionales (`extra="forbid"`). Las propiedades de entrada no enviadas se representan internamente como ausentes o nulas; el contrato operativo es:

| Campo | Tipo validado / valor predeterminado | Uso |
|---|---|---|
| `cidr` | cadena | Forma directa CIDR. |
| `address` | cadena IPv4 | Primera parte de la forma directa por dirección y máscara. |
| `netmask` | cadena IPv4 | Máscara contigua de la forma directa por dirección y máscara. |
| `required_hosts` | entero estricto `>= 1` | Activa el cálculo inverso. |
| `mode` | `conventional` o `point-to-point`; default `conventional` | Opcional en directo y obligatorio en inverso. |

### Cálculo directo

Se acepta una de estas formas:

~~~json
{
  "cidr": "192.168.1.5/24",
  "mode": "conventional"
}
~~~

o:

~~~json
{
  "address": "192.168.1.5",
  "netmask": "255.255.255.0",
  "mode": "conventional"
}
~~~

`cidr` debe ser una cadena con IPv4 y prefijo de 0 a 32. `address` y `netmask` deben ser cadenas IPv4; la máscara debe ser contigua. Las direcciones con bits de host activos se normalizan a la red. `mode` es opcional en el cálculo directo y su valor predeterminado es `conventional`; valores admitidos: `conventional` y `point-to-point`.

### Cálculo inverso

~~~json
{
  "required_hosts": 3,
  "mode": "point-to-point"
}
~~~

`required_hosts` debe ser un entero estricto mayor o igual que 1. Para el cálculo inverso, `mode` debe enviarse explícitamente y debe ser uno de los dos valores admitidos. Las formas directa e inversa son incompatibles; también lo son `cidr` con `address` o `netmask`. No se admite `ip` + `prefix`.

## Respuestas exitosas

### Cálculo directo (200)

La respuesta contiene `network`, `broadcast`, `netmask`, `wildcard`, `first_usable`, `last_usable`, `total_addresses`, `usable_addresses`, `binary` y `warnings`. `total_addresses` es el tamaño matemático del bloque y `usable_addresses` su capacidad efectiva según el modo.

- En modo `conventional`, `/0` a `/30` reservan red y broadcast; `/31` y `/32` tienen cero direcciones utilizables. Para `/31` y `/32`, `broadcast`, `first_usable` y `last_usable` son `null`.
- En modo `point-to-point`, `/31` tiene dos direcciones utilizables y `/32` una. En ambos casos `broadcast` es `null`; los límites utilizables son las direcciones del bloque.
- Para otros prefijos, `point-to-point` aplica el comportamiento convencional y agrega `point_to_point_not_applicable`.
- Si la entrada contenía bits de host activos, la dirección se normaliza a la red y se agrega `host_bits_normalized`.

Los warnings están en la raíz y son objetos `{ "code": string, "message": string }`. La clasificación no forma parte de la respuesta pública actual y permanece aplazada.

| Campo directo | Tipo de respuesta | Nulabilidad |
|---|---|---|
| `network`, `netmask`, `wildcard` | cadena IPv4 | No nulos. |
| `broadcast` | cadena IPv4 o null | Null para `/31` y `/32`. |
| `first_usable`, `last_usable` | cadena IPv4 o null | Null cuando la capacidad utilizable es cero. |
| `total_addresses`, `usable_addresses` | entero | No nulos; total matemático y capacidad efectiva, respectivamente. |
| `binary` | objeto con seis valores `string | null` | Cada clave corresponde al campo IPv4 homónimo y conserva su nulabilidad. |
| `warnings` | lista de objetos `{code, message}` | Siempre presente; puede estar vacía. |

Ejemplo ilustrativo para `/31` en modo punto a punto:

~~~json
{
  "network": "192.0.2.0",
  "broadcast": null,
  "netmask": "255.255.255.254",
  "wildcard": "0.0.0.1",
  "first_usable": "192.0.2.0",
  "last_usable": "192.0.2.1",
  "total_addresses": 2,
  "usable_addresses": 2,
  "binary": {
    "network": "11000000.00000000.00000010.00000000",
    "broadcast": null,
    "netmask": "11111111.11111111.11111111.11111110",
    "wildcard": "00000000.00000000.00000000.00000001",
    "first_usable": "11000000.00000000.00000010.00000000",
    "last_usable": "11000000.00000000.00000010.00000001"
  },
  "warnings": [
    {
      "code": "host_bits_normalized",
      "message": "La dirección contenía bits de host; se calculó la dirección de red."
    }
  ]
}
~~~

`binary` tiene exactamente seis claves: `network`, `broadcast`, `netmask`, `wildcard`, `first_usable` y `last_usable`. Los valores no nulos son cuatro grupos de ocho bits separados por puntos; los valores correspondientes a campos IPv4 nulos también son `null`.

### Cálculo inverso (200)

La respuesta contiene `required_hosts`, `mode_requested`, `mode_applied`, `prefix`, `total_addresses`, `usable_addresses` y `warnings`; no contiene dirección de red ni `binary`.

| Campo inverso | Tipo de respuesta | Nulabilidad |
|---|---|---|
| `required_hosts`, `prefix`, `total_addresses`, `usable_addresses` | entero | No nulos. |
| `mode_requested`, `mode_applied` | `conventional` o `point-to-point` | No nulos. |
| `warnings` | lista de objetos `{code, message}` | Siempre presente; puede estar vacía. |

Se recorren los prefijos desde `/32` hasta `/0` y se elige el de mayor longitud cuya capacidad efectiva satisface `required_hosts`. La capacidad convencional máxima en `/0` es 4,294,967,294; una solicitud superior produce `insufficient_capacity`. `mode_requested` refleja la solicitud. `mode_applied` solo es `point-to-point` cuando el modo fue solicitado y el prefijo seleccionado es `/31` o `/32`; si no, es `conventional`. Se agrega `point_to_point_not_applicable` cuando se solicitó `point-to-point` y el prefijo elegido no es `/31` ni `/32`.

~~~json
{
  "required_hosts": 3,
  "mode_requested": "point-to-point",
  "mode_applied": "conventional",
  "prefix": 29,
  "total_addresses": 8,
  "usable_addresses": 6,
  "warnings": [
    {
      "code": "point_to_point_not_applicable",
      "message": "Point-to-point no aplica al prefijo seleccionado; se aplicó conventional."
    }
  ]
}
~~~

## Errores

Todas las respuestas de error tienen las claves `error` y `detail`, ambas cadenas. Los detalles conocidos de validación y de dominio se generan en español; algunos errores HTTP delegan el texto de `detail` al framework, como se indica abajo.

| HTTP | Código | Condición y detalle implementados |
|---|---|---|
| 400 | `invalid_json` | La capa HTTP produce un `400` (por ejemplo, bytes UTF-8 inválidos al interpretar el JSON o error al leer el cuerpo). Detalle actual: `El cuerpo de la petición no es JSON válido.` |
| 404 | `not_found` | Ruta inexistente. Detalle actual: `Recurso no encontrado.` |
| 405 | `method_not_allowed` | Método no permitido. El handler conserva el detalle recibido de Starlette. |
| 415 | `unsupported_media_type` | Falta `Content-Type` o no es `application/json`. El detalle incluye el valor recibido y el tipo esperado. |
| 422 | `invalid_json` | Error de sintaxis JSON informado por la validación de solicitud de FastAPI. Detalle actual: `El cuerpo de la petición no es JSON válido.` |
| 422 | `invalid_body` | El valor JSON superior no se puede tratar como objeto de entrada. El detalle deriva del error de validación de Pydantic. |
| 422 | `unknown_field` | Uno o más campos no declarados. Los nombres múltiples se ordenan alfabéticamente en el detalle. |
| 422 | `incompatible_inputs` | Se mezclan cálculo directo e inverso o formas directas mutuamente excluyentes. |
| 422 | `missing_field` | Falta una forma de entrada completa, un miembro de `address` + `netmask` o `mode` en el cálculo inverso. |
| 422 | `invalid_type` | El tipo de un campo no coincide con el requerido. |
| 422 | `invalid_value` | IPv4, prefijo, modo o valor numérico inválido. |
| 422 | `non_contiguous_netmask` | Una máscara IPv4 válida sintácticamente no tiene unos contiguos a la izquierda. |
| 422 | `insufficient_capacity` | `required_hosts` supera la capacidad efectiva máxima de `/0`. |
| 500 | `internal_error` | Excepción no controlada; detalle actual: `Error interno del servidor.` No se incluye el texto de la excepción. |
| 422 | `validation_error` | Respaldo si FastAPI entrega un `RequestValidationError` sin errores; detalle actual: `Error de validación en la petición.` |
| estado HTTP distinto de los mapeados | `http_<status>` | Respaldo del handler HTTP; el detalle se toma de la excepción si está presente. |

Ejemplo de respuesta de campo desconocido:

~~~json
{
  "error": "unknown_field",
  "detail": "Campo desconocido: 'foo'."
}
~~~

El handler Pydantic prioriza los errores de campo desconocido cuando aparecen junto con otros errores de validación; si hay varios, los agrupa y ordena. El modelo ejecuta las comprobaciones de incompatibilidad y campos faltantes en el orden definido en `models.py`. Las pruebas fuente incluyen casos para método antes de cuerpo malformado, tipo de contenido no admitido antes de interpretar JSON, campo desconocido frente a incompatibilidad, incompatibilidad frente a falta de campo o tipo inválido, falta frente a tipo inválido y tipo/valor frente a máscara no contigua. Esas pruebas están presentes en el repositorio; este texto no afirma que hayan sido ejecutadas en esta actualización.

### Diferencia respecto del contrato documentado anteriormente

Una versión anterior de este documento excluía HTTP 400 y asignaba `invalid_json` a 422 en general. El código actual distingue: los errores de sintaxis JSON mapeados como `RequestValidationError` responden 422, mientras que los `HTTPException` 400 responden `invalid_json`/400. La prueba existente de bytes UTF-8 inválidos espera 400. Esta documentación registra ese comportamiento implementado; no acredita que la excepción de HTTP 400 haya sido formalmente aprobada como cambio de diseño.
