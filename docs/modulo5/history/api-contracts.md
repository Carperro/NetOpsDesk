# Contrato de API — Historial de diagnósticos

> Contrato objetivo actualizado con las resoluciones aprobadas; pendiente de implementación y verificación OpenAPI.

## Modelo de entrada y salida

La respuesta de una entrada contiene `id`, `tool_name`, `action`, `result_status`, `details` y `created_at`. `id` y `created_at` se generan al crear. `tool_name` y `action` son obligatorios; `details` es opcional y su default es `""`. `result_status` forma parte de los datos de la entrada, pero su obligatoriedad en el request aún debe confirmarse.

## Operación: listar historial

- **Método y ruta:** `GET /api/v1/tools/history/logs`
- **Propósito:** listar las entradas de la más reciente a la más antigua.
- **Solicitud:** sin parámetros ni body.
- **Respuesta objetivo:** HTTP `200 OK`, array JSON directo; sin entradas devuelve `[]`.
- **Orden SQL:** `ORDER BY created_at DESC, id DESC`.

```json
[
  {
    "id": 12,
    "tool_name": "ping",
    "action": "Diagnóstico de conectividad",
    "result_status": "success",
    "details": "Respuesta recibida desde 192.0.2.1",
    "created_at": "2026-10-20T14:30:00.123456"
  }
]
```

`created_at` se genera mediante `datetime.now().isoformat()` y se almacena como `TEXT`.

## Operación: crear entrada

- **Método y ruta:** `POST /api/v1/tools/history/logs`
- **Content-Type:** `application/json`.
- **Solicitud:** `tool_name` y `action` son obligatorios. `details` es opcional y toma `""` si se omite. `result_status` se recibe como `TEXT`, pero su obligatoriedad aún debe confirmarse.

```json
{
  "tool_name": "ping",
  "action": "Diagnóstico de conectividad",
  "result_status": "success"
}
```

- **Respuesta objetivo:** HTTP `201 Created` con el registro creado, incluido `id`, `details` normalizado y `created_at`.

## Operación: eliminar una entrada

- **Método y ruta:** `DELETE /api/v1/tools/history/logs/{id}`
- **Solicitud:** ID entero en la ruta; sin body.
- **Respuesta objetivo:** HTTP `204 No Content`.
- **Error:** HTTP `422`, código `not_found`, si el ID no existe.

## Operación: limpiar historial

- **Método y ruta:** `DELETE /api/v1/tools/history/logs`
- **Solicitud:** sin parámetros ni body.
- **Respuesta objetivo:** HTTP `204 No Content` después de eliminar todas las filas de `history`; no se modifican las demás tablas de `netops.db`.

## Errores

| HTTP | Código `error` | Cuándo ocurre |
|---|---|---|
| 422 | `not_found` | El ID solicitado para eliminar no existe. |
| 422 | Errores de esquema según contrato común | `tool_name` o `action` ausentes, o request inválido conforme al modelo definitivo. |
| 429 | `too_many_requests` | No hay permisos disponibles en `asyncio.Semaphore(5)`. |

Los errores deben usar el sobre común aplicable al Módulo 5. No se asume automáticamente que DEC-012, limitada al Módulo 1, rija este contrato.

## Concurrencia

Las operaciones usan `asyncio.Semaphore(5)`. Si no hay permisos disponibles, la API responde HTTP `429` con código `too_many_requests`.

## Compatibilidad y verificación

- **OpenAPI:** cuatro operaciones: GET colección, POST colección, DELETE por `{id}` y DELETE de colección. Pendiente de verificar al implementar.
- **Pruebas de contrato:** pendientes; cubrir `200`, `201`, `204`, `422 not_found`, validación de campos requeridos y respuesta `429 too_many_requests`.
- **Cambios incompatibles o pendientes:** confirmar obligatoriedad de `result_status` y fijar el contrato común de errores de esquema del Módulo 5.