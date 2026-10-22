# Contrato de API — Estado de adaptadores

> Contrato objetivo de una herramienta pendiente de implementación e integración según el catálogo.

## Operación: listar adaptadores locales

- **Método y ruta:** `GET /api/v1/tools/adapters/execute`
- **Propósito:** devolver el estado operativo, la velocidad, el MTU y el soporte de multicast de los adaptadores del servidor que ejecuta NetOps Desk.
- **Content-Type:** sin request body; no se requieren parámetros.

### Solicitud

No se envían parámetros ni cuerpo.

### Respuesta correcta

- **Estado:** HTTP `200 OK` cuando la consulta se completa.
- **Esquema:** objeto raíz con array `adapters`.

```json
{
  "adapters": [
    {
      "name": "Ethernet",
      "is_up": true,
      "speed_mbps": 1000,
      "mtu": 1500,
      "is_multicast": true
    }
  ]
}
```

| Campo | Tipo | Semántica |
|---|---|---|
| `adapters` | array | Adaptadores locales devueltos por el runner. |
| `adapters[].name` | string | Nombre del adaptador informado por el sistema. |
| `adapters[].is_up` | boolean | Estado operativo del adaptador informado por psutil. |
| `adapters[].speed_mbps` | integer | Velocidad en Mbps; `0` cuando el sistema no informa la velocidad. |
| `adapters[].mtu` | integer | Unidad máxima de transmisión del adaptador. |
| `adapters[].is_multicast` | boolean | Indica si el adaptador soporta multicast según las banderas de psutil; `false` cuando la versión de psutil no provee el flag. |

La respuesta describe la máquina servidor, no el navegador.

### Casos de respuesta especiales

- **Sin adaptadores:** la consulta devuelve HTTP `200 OK` con `"adapters": []`.
- **Velocidad no informada:** `speed_mbps` vale `0`.
- **Multicast no disponible:** `is_multicast` vale `false`.

### Errores

Los errores siguen el sobre común `{ "error": "<código>", "detail": "<mensaje>" }`, según `docs/modulo1/api-contracts.md` y las decisiones vigentes. Los mensajes destinados a la interfaz deben estar en español y no revelar detalles internos.

| HTTP | Código `error` | Cuándo ocurre | `detail`/mensaje esperado |
|---|---|---|---|
| 422 | `execution_failed` | `psutil` falla al consultar `net_if_stats()` o el runner produce un error de dominio | Mensaje en español indicando que no se pudo obtener el estado de los adaptadores, sin exponer excepciones ni rutas internas |
| 429 | `too_many_requests` | El semáforo `asyncio.Semaphore(5)` se agota | Mensaje en español indicando que se alcanzó el límite de consultas concurrentes |

## Compatibilidad y verificación

- **OpenAPI:** operación GET sin body; el modelo de salida debe reflejar exactamente los nombres y tipos aquí documentados.
- **Pruebas de contrato:** pendientes de implementación; deben comprobar respuesta vacía (`adapters: []`), uno o más adaptadores, velocidad no informada (`0`), multicast no disponible (`false`), error `execution_failed` (422) y saturación del semáforo (429).
- **Cambios incompatibles o pendientes:** Ninguno.