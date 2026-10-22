# Contrato de API — Analizador de direcciones MAC

> Contrato objetivo de la herramienta 18, pendiente de implementación. El catálogo registra la herramienta como pendiente de desarrollo e integración.

## Operación: analizar una dirección MAC

- **Método y ruta:** `POST /api/v1/tools/mac-analyzer/execute`
- **Propósito:** validar y normalizar una MAC y obtener su fabricante desde la base OUI local.
- **Content-Type:** `application/json`.

### Solicitud

```json
{
  "mac": "00:1A:2B:3C:4D:5E"
}
```

| Campo | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| `mac` | string | Sí | Seis octetos hexadecimales separados por dos puntos o guiones; se admiten mayúsculas y minúsculas. |

### Respuesta correcta

- **Estado:** HTTP `200 OK` cuando la entrada es válida, incluso si no hay coincidencia de fabricante.
- **Esquema:** objeto con la entrada original, forma canónica y fabricante.

```json
{
  "mac_original": "00:1A:2B:3C:4D:5E",
  "mac_normalized": "00:1a:2b:3c:4d:5e",
  "vendor": "Cisco Systems, Inc"
}
```

`mac_normalized` siempre usa minúsculas y dos puntos. `vendor` contiene el fabricante encontrado en la base OUI local o `Desconocido` si no hay coincidencia. La identificación no prueba propiedad, ubicación ni uso actual del dispositivo.

### Errores

| HTTP | Código `error` | Cuándo ocurre | `detail`/mensaje esperado |
|---|---|---|---|
| 422 | `invalid_mac` | La MAC no contiene seis octetos hexadecimales en un formato admitido. El handler global traduce el `DomainError` a HTTP 422. | Mensaje en español que indique que el formato de MAC no es válido. |
| 429 | `too_many_requests` | Los cinco permisos del semáforo están ocupados; la solicitud se rechaza sin esperar. | Mensaje en español que indique que se alcanzó el límite de consultas concurrentes. |

El error de dominio `invalid_mac` se traduce a HTTP 422 mediante el handler global. Los errores usan el sobre `{ "error": "<código>", "detail": "<mensaje>" }`, tomando como referencia [`docs/modulo1/api-contracts.md`](../../modulo1/api-contracts.md); los mensajes de esta herramienta deben estar en español.

## Concurrencia

La capa API usa `asyncio.Semaphore(5)` y rechaza inmediatamente la solicitud cuando no hay permiso disponible, con HTTP `429` y código `too_many_requests`. El semáforo limita dentro de su proceso/event loop; no coordina varios workers.

## Compatibilidad y verificación

- **OpenAPI:** operación POST con un campo de entrada `mac` y tres campos de salida exactamente como en el ejemplo.
- **Pruebas de contrato:** pendientes de implementación; deberán verificar formatos válidos, errores de formato, fabricante encontrado y ausencia de coincidencia.
- **Cambios incompatibles o pendientes:** definir el alcance del límite al operar con varios workers y formalizar el contrato transversal de errores del Módulo 4.
