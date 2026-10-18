# Contrato de API — Detector de solapamiento de redes

Las reglas comunes de formato y semántica de errores están en [`../api-contracts.md`](../api-contracts.md).

## Calcular solapamientos

- **Método y ruta:** `POST /api/v1/tools/overlap/calculate`
- **Content-Type:** `application/json`
- **Descripción:** compara dos o más redes IPv4 CIDR.

### Solicitud

```json
{
  "networks": ["192.0.2.0/24", "192.0.2.64/26"]
}
```

| Campo | Tipo | Requerido | Restricciones observadas |
|---|---|---|---|
| `networks` | lista de cadenas | Sí | Entre 2 y 50 elementos. Cada elemento debe poder interpretarse como red IPv4 CIDR por el dominio. Los campos adicionales del objeto se rechazan. |

Una solicitud con más de 50 redes responde HTTP `422` con el código `invalid_network`.

El dominio usa `strict=False`: los bits de host se normalizan durante la comparación. La respuesta `networks` conserva las cadenas originales recibidas.

### Respuesta correcta — HTTP 200

```json
{
  "networks": ["192.0.2.0/24", "192.0.2.64/26"],
  "has_overlap": true,
  "overlaps": [
    {
      "network_a": "192.0.2.0/24",
      "network_b": "192.0.2.64/26",
      "message": "La red 192.0.2.64/26 está completamente dentro de 192.0.2.0/24."
    }
  ]
}
```

| Campo | Tipo | Semántica |
|---|---|---|
| `networks` | lista de cadenas | Entrada original, incluidos los bits de host si se proporcionaron. |
| `has_overlap` | booleano | `true` si se encontró al menos un par solapado. |
| `overlaps` | lista de objetos | Un elemento por cada par conflictivo, respetando el orden de combinaciones de entrada. |
| `overlaps[].network_a` | cadena | Red normalizada del primer miembro del par. |
| `overlaps[].network_b` | cadena | Red normalizada del segundo miembro del par. |
| `overlaps[].message` | cadena | Explicación en español de contención o solapamiento parcial. |

Las redes adyacentes no se consideran solapadas. Una red igual a otra se representa como contención según el orden de entrada y la lógica actual.

### Errores

Todos usan el sobre común `{ "error": "<código>", "detail": "<mensaje>" }`.

| HTTP | Código | Condición |
|---|---|---|
| `400` | `invalid_json` | El cuerpo crudo no puede leerse/decodificarse como JSON, según DEC-007 y el handler común. |
| `405` | `method_not_allowed` | Método distinto de POST en la ruta. |
| `415` | `unsupported_media_type` | Content-Type distinto de `application/json`. |
| `422` | `too_few_networks` | Se proporcionaron menos de dos redes. |
| `422` | `invalid_network` | Una red no es un CIDR IPv4 válido, incluida una dirección IPv6. |
| `422` | `invalid_type`, `invalid_value`, `unknown_field` u otro código de esquema | Error de validación del modelo de API. Los detalles se generan en español. |
| `500` | `internal_error` | Excepción inesperada; detalle público genérico. |

La tabla refleja los handlers globales. Las pruebas específicas de Overlap cubren 200, 405, 415 y 422; el comportamiento 400/500 se define en las capas comunes y no tiene caso específico en `tests/test_api_overlap.py`.
