# Contrato de API — Traceroute

> Contrato objetivo derivado de la solicitud del usuario. La ruta no está implementada y no se ha verificado OpenAPI. Las reglas HTTP específicas marcadas como propuestas requieren formalización del contrato común para Módulo 2 antes de presentar el contrato como verificado.

## Operación: ejecutar traceroute

- **Método y ruta:** `POST /api/v1/tools/traceroute/execute`.
- **Propósito:** observar los saltos que responden en la ruta a un destino.
- **Content-Type:** `application/json`.

### Solicitud

```json
{
  "host": "8.8.8.8",
  "max_hops": 15
}
```

| Campo | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| `host` | string | Sí | IPv4, IPv6 o dominio según las reglas estrictas de host de Ping. No URL, puerto, CIDR, zone ID, espacios, controles ni metacaracteres de shell. |
| `max_hops` | integer estricto | No | Default `15`; mínimo `1`, máximo `30`. No aceptar booleanos como enteros. |

Se propone rechazar campos adicionales (`extra="forbid"`) y devolver error de esquema; la política debe confirmarse al definir el modelo API. No admitir parámetros de proceso del lado cliente.

### Respuesta correcta

- **Estado:** `200` cuando el proceso termina al llegar al destino o al alcanzar `max_hops` y la salida se puede interpretar, aunque algunos saltos no respondan.
- **Esquema:** host original, IP del destino elegida por Windows y lista ordenada de saltos observados.

```json
{
  "host": "8.8.8.8",
  "resolved_ip": "8.8.8.8",
  "hops": [
    {
      "hop_number": 1,
      "ip": "192.168.1.1",
      "times_ms": [1.0, 1.0, 2.0]
    },
    {
      "hop_number": 2,
      "ip": null,
      "times_ms": []
    }
  ]
}
```

La respuesta contiene exactamente los campos raíz `host`, `resolved_ip` y `hops`; cada salto contiene `hop_number`, `ip` y `times_ms`. `ip` es una dirección canonicalizada o `null`. `times_ms` contiene los RTT numéricos extraídos de esa fila. Una fila totalmente perdida no se omite: se incluye con `ip: null` y `times_ms: []`. Una fila parcialmente respondida incluye solo los tiempos recibidos, en orden y sin rellenar los probes perdidos con `null`; ver [decision-log.md](decision-log.md).

| Campo | Tipo | Semántica |
|---|---|---|
| `host` | string | Host entregado en la solicitud. |
| `resolved_ip` | string | Dirección final que Windows resolvió/seleccionó para la traza; no se reemplaza por el nombre original. |
| `hops` | array | Filas de salto parseadas en orden; un router que no respondió puede permanecer en la lista con IP nula. |
| `hop_number` | integer | Número mostrado al inicio de la fila de `tracert.exe`, dentro del límite solicitado. |
| `ip` | string o `null` | IP del router si aparece y se valida; `null` cuando no hay IP parseable. |
| `times_ms` | array de number | RTT numéricos en milisegundos disponibles para la fila. Las sondas `*` no se convierten en tiempos ni en strings. |

Una fila con una respuesta de tres devuelve, por ejemplo, `times_ms: [12.0]`; con dos respuestas devuelve `[12.0, 14.5]`. Una fila sin respuesta devuelve `ip: null` y `times_ms: []`. Todos los saltos observados se conservan en orden ascendente de `hop_number`.

### Errores

Se propone el sobre común `{ "error": "<código>", "detail": "<mensaje en español>" }`, siguiendo el patrón documentado en DEC-012 y `docs/modulo1/api-contracts.md`. DEC-012 formaliza Módulo 1; su extensión normativa a Módulo 2 debe confirmarse al integrar.

| HTTP | Código `error` | Cuándo ocurre | Estado |
|---|---|---|---|
| `400` | `invalid_json` | El cuerpo no se puede leer o decodificar como JSON (DEC-007, si aplica al módulo). | Pendiente de confirmar la convención Módulo 2 |
| `415` | `unsupported_media_type` | Content-Type no admitido. | Pendiente de confirmar la convención Módulo 2 |
| `422` | `invalid_type`, `missing_field`, `unknown_field`, `invalid_host`, `invalid_max_hops` | JSON o valores no válidos; `max_hops` debe ser entero entre 1 y 30. | Estados y códigos específicos aprobados por el usuario; el sobre común Módulo 2 sigue pendiente de formalización |
| `429` | `too_many_requests` | Ya hay tres trazas ocupando el semáforo global y no se admite la nueva solicitud. | APROBADO; un único worker Uvicorn mantiene el límite global |
| `500` | `execution_failed` | No se puede iniciar o ejecutar `tracert.exe`. | APROBADO; detalle público seguro |
| `500` | `internal_error` | Fallo inesperado no clasificado; detalle público genérico. | Convención del proyecto; confirmar formalización Módulo 2 |
| `504` | `traceroute_timeout` | El subprocess supera 30 segundos y se termina. | APROBADO; detalle público en español |

No se devolverán salida cruda, argumentos ejecutados, trazas ni rutas locales. El status/código ante exceso del límite de 64 KiB de stdout sigue pendiente de decisión.

## Compatibilidad y verificación

- **OpenAPI:** pendiente; la operación no existe todavía.
- **Pruebas de contrato:** pendientes; los nombres de archivos de prueba son objetivos, no archivos existentes.
- **Cambios incompatibles o pendientes:** política de campos extra, error de exceso de stdout, formalización del sobre común de errores para Módulo 2 y semántica de familia al resolver dominios.
