# Contrato de API — Gestor de direcciones IP (IPAM)

> Contrato aprobado; modelos, dominio, repositorio, ruta y pruebas están presentes en el árbol de trabajo, y `api/main.py` registra el router allí. Los cambios de código no forman parte de este commit documental y el semáforo aprobado aún no está implementado en la ruta.

## Modelo de datos

| Campo | Tipo | Request | Response | Semántica |
|---|---|---|---|---|
| `id` | integer | No | Sí | Identificador del registro |
| `ip_address` | string | Sí | Sí | IPv4 válida y única en la tabla |
| `status` | string | Sí | Sí | Enum: `available`, `assigned`, `reserved` |
| `assigned_to` | string | No, default `""` | Sí | Destino/persona/equipo asignado |
| `notes` | string | No, default `""` | Sí | Observaciones |

Los nombres de campos del request y response son los mismos salvo `id`, que se genera al crear. La política para campos desconocidos seguirá el modelo común del proyecto (`extra="forbid"`) al implementar.

## Operación: listar direcciones

- **Método y ruta:** `GET /api/v1/tools/ipam/addresses`
- **Solicitud:** sin parámetros ni body.
- **Respuesta:** `200 OK`, lista JSON directa. Sin registros, `[]`.

```json
[
  {
    "id": 1,
    "ip_address": "192.168.1.20",
    "status": "assigned",
    "assigned_to": "Impresora recepción",
    "notes": "Planta baja"
  }
]
```

Los campos `assigned_to` y `notes` son opcionales. Si se omiten, la API usa la cadena vacía `""`.

## Operación: crear dirección

- **Método y ruta:** `POST /api/v1/tools/ipam/addresses`
- **Content-Type:** `application/json`.
- **Solicitud:** `ip_address` y `status` son requeridos; `assigned_to` y `notes` son opcionales y por defecto `""`.

```json
{
  "ip_address": "192.168.1.20",
  "status": "assigned",
  "assigned_to": "Impresora recepción",
  "notes": "Planta baja"
}
```

- **Respuesta objetivo:** `201 Created` con el registro creado e `id`.

## Operación: editar dirección

- **Método y ruta:** `PUT /api/v1/tools/ipam/addresses/{id}`
- **Content-Type:** `application/json`.
- **Solicitud:** ID entero en la ruta. `ip_address` y `status` son requeridos; `assigned_to` y `notes` son opcionales y por defecto `""`.
- **Semántica:** PUT reemplaza todos los campos del registro. Si se omite `assigned_to` o `notes`, el valor existente se reemplaza por `""`; no es una actualización parcial.
- **Respuesta objetivo:** `200 OK` con el registro actualizado.

## Operación: eliminar dirección

- **Método y ruta:** `DELETE /api/v1/tools/ipam/addresses/{id}`
- **Solicitud:** sin body; ID entero en la ruta.
- **Respuesta objetivo:** `204 No Content`.

## Errores

Las respuestas de error usan el sobre común `{ "error": "<código>", "detail": "<mensaje en español>" }`.

| HTTP | Código `error` | Condición |
|---|---|---|
| `422` | `invalid_ip` | `ip_address` no es una IPv4 válida |
| `422` | `invalid_status` | `status` no pertenece a `available`, `assigned`, `reserved` |
| `422` | `duplicate_ip` | Otra fila ya registra la dirección; aplica al crear y al editar |
| `422` | `not_found` | ID inexistente al editar o eliminar |
| `429` | `too_many_requests` | Los cinco permisos del semáforo están ocupados; la solicitud se rechaza sin esperar |
| `422` | `missing_field`, `unknown_field`, `invalid_type` o `invalid_value` | Validación de esquema de la solicitud según el contrato común |
| `415` | `unsupported_media_type` | Tipo de contenido no admitido en POST/PUT |
| `500` | `internal_error` | Fallo inesperado, con detalle público genérico |

Los errores de dominio son traducidos por `domain_error_handler`; el dominio no asigna códigos HTTP.

## Compatibilidad y verificación

- **Contrato común:** [API del Módulo 1](../../modulo1/api-contracts.md), como referencia existente para el sobre JSON y la semántica de errores; confirmar su alcance para Módulo 4 al integrar.
- **Pruebas:** [test-strategy.md](test-strategy.md). Existen pruebas de dominio, repositorio y API sin seguimiento por Git; no se ejecutaron pruebas durante esta tarea.
- **Pendientes:** orden de listado, reglas de canonicalización IPv4 y alcance del semáforo entre varios workers.
- **Brecha observada:** el router presente no registra `asyncio.Semaphore(5)` ni produce `429 too_many_requests`. Ese estado está aprobado contractualmente y aún no coincide con la ruta.
