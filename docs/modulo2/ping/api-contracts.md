# Contrato de API — Ping

> Contrato de diseño; no hay ruta Ping implementada ni OpenAPI verificado. El contrato debe confirmarse al integrar la herramienta con la aplicación.

## Operación: ejecutar ping

- **Método y ruta:** `POST /api/v1/tools/ping/execute`.
- **Propósito:** ejecutar una prueba ICMP acotada contra un host.
- **Content-Type:** `application/json`.

### Solicitud

```json
{
  "host": "8.8.8.8",
  "count": 4
}
```

| Campo | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| `host` | string | Sí | Una IPv4, IPv6 o hostname que cumpla RFC 1123. No acepta URL, puerto, CIDR, brackets IPv6, zone ID, espacios, controles, CR/LF ni metacaracteres de shell. La validación se repite en dominio antes de invocar el runner. |
| `count` | integer estricto | No | Default `4`; mínimo `1`, máximo `10`. Booleanos no se aceptan como enteros. |

Campos adicionales se deben rechazar con el código de esquema común `unknown_field`. El hostname se resuelve durante la ejecución del runner; `resolved_ip` identifica la dirección seleccionada realmente por `ping.exe`, no una promesa de disponibilidad DNS futura.

### Respuesta correcta

- **Estado:** `200` cuando la ejecución completa y el resultado se puede interpretar, incluso si no hubo respuestas ICMP.
- **Esquema:** cantidades de paquetes, pérdida porcentual, latencias en milisegundos y respuestas individuales.

```json
{
  "host": "8.8.8.8",
  "resolved_ip": "8.8.8.8",
  "packets_sent": 4,
  "packets_received": 2,
  "packet_loss_percent": 50.0,
  "min_ms": 12.0,
  "max_ms": 15.0,
  "avg_ms": 13.5,
  "responses": [
    {"seq": 1, "time_ms": 12.0},
    {"seq": 2, "time_ms": 15.0}
  ]
}
```

El ejemplo es ilustrativo; el sistema operativo puede reportar resolución temporal entera. `responses` contiene solo respuestas recibidas. `seq` es un ordinal consecutivo asignado por el parser a cada respuesta exitosa, comenzando en 1. No es el número de secuencia ICMP ni el índice de intento: si se envían 4 paquetes y se reciben 3, las respuestas tendrán `seq` 1, 2 y 3, sin huecos. El parser no adivina qué intento se perdió. Un RTT reportado como `<1ms` se representa como el número `0.0`; los campos de tiempo nunca contienen strings.

Ejemplo de ejecución completada sin respuestas ICMP:

```json
{
  "host": "192.0.2.10",
  "resolved_ip": "192.0.2.10",
  "packets_sent": 4,
  "packets_received": 0,
  "packet_loss_percent": 100.0,
  "min_ms": null,
  "max_ms": null,
  "avg_ms": null,
  "responses": []
}
```

| Campo | Tipo | Semántica |
|---|---|---|
| `host` | string | Valor de host enviado por el cliente, sin usarlo como HTML ni como fragmento de comando. |
| `resolved_ip` | string | IP literal seleccionada por la ejecución, normalizada; no se devuelve el hostname como sustituto. |
| `packets_sent` | integer | Cantidad solicitada si el proceso completó la operación. |
| `packets_received` | integer | Cantidad de respuestas Echo válidas interpretadas. |
| `packet_loss_percent` | number | `(packets_sent - packets_received) / packets_sent * 100`. |
| `min_ms`, `max_ms`, `avg_ms` | number o `null` | Estadísticas de las respuestas recibidas; `null` si no hay ninguna. No incluir latencias de timeout. |
| `responses` | array | Respuestas válidas ordenadas, cada una con `seq` consecutivo 1..N y `time_ms` numérico. Para un RTT `<1ms`, `time_ms` es `0.0`. |

Si la operación concluye sin respuestas, devuelve `200`, `packets_received: 0`, `packet_loss_percent: 100.0`, `responses: []` y latencias `null`. Esto comunica que la medición se realizó pero el destino no respondió; no prueba por sí solo que el host esté desconectado.

### Errores

El sobre previsto es `{ "error": "<código>", "detail": "<mensaje en español>" }`, alineado con el handler común de la aplicación. DEC-012 describe formalmente el contrato del Módulo 1; la aplicación de su alcance a Módulo 2 debe confirmarse al incorporar la ruta.

| HTTP | Código `error` | Cuándo ocurre | Estado |
|---|---|---|---|
| `400` | `invalid_json` | El cuerpo no puede leerse/decodificarse según DEC-007. | Compatible con la convención global vigente; confirmar integración Módulo 2. |
| `415` | `unsupported_media_type` | Content-Type distinto de `application/json`. | Esperado según dependencia común; ruta aún no implementada. |
| `422` | `invalid_type`, `invalid_value`, `missing_field`, `unknown_field` | Error de esquema de solicitud, incluidos los límites Pydantic de `count`. | Esperado según handler común. |
| `422` | `invalid_host`, `invalid_count` | Host inválido o `count` fuera de 1–10. | Validación de entrada según DEC-012. |
| `429` | `too_many_requests` | Ya hay cinco ejecuciones ocupando el semáforo global y no se admite la nueva solicitud. | La ruta no deja solicitudes excedentes esperando sin límite; requiere un único worker Uvicorn para mantener el límite global. |
| `500` | `execution_failed` | No se puede iniciar o completar la ejecución del binario por un fallo del sistema, por ejemplo `ping.exe` no encontrado. | Detalle público seguro; no exponer salida cruda ni rutas internas. |
| `500` | `internal_error` | Fallo inesperado no clasificado como error de ejecución. | Detalle público genérico. |
| `504` | `ping_timeout` | El subprocess supera el límite total de 15 segundos y se termina. | Error de gateway; detalle público en español. |

Una pérdida de paquetes no es un error HTTP si la ejecución finaliza y se obtiene un resultado interpretable. No se devolverán argumentos de proceso, salidas crudas, trazas ni rutas internas en `detail`.

## Compatibilidad y verificación

- **OpenAPI:** pendiente; el endpoint todavía no existe.
- **Pruebas de contrato:** pendientes; no hay `tests/test_api_ping.py`.
- **Conformidad prevista:** semántica de `seq`, caso sin respuesta y códigos/estados Ping se fijan en este contrato y en [decision-log.md](decision-log.md). Siguen pendientes la verificación OpenAPI y de pruebas al implementar, la formalización transversal del contrato común de Módulo 2 y la política de nombres IDN/punto final.
