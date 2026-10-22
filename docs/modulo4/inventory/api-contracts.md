# Contrato de API — Inventario de dispositivos

> Contrato contrastado estáticamente con `DeviceInput`, `DeviceOutput`, las rutas CRUD y los handlers globales. No se ejecutaron pruebas durante esta revisión.

## Modelo de datos

La respuesta de un dispositivo contiene exactamente estos campos:

| Campo | Tipo | Request | Response | Semántica |
|---|---|---|---|---|
| `id` | integer | No | Sí | Identificador autoincremental; no se acepta en el cuerpo de entrada (`extra="forbid"`) |
| `name` | string | Sí | Sí | Obligatorio; el dominio elimina espacios externos y rechaza valor vacío/blanco |
| `ip_address` | string | Sí | Sí | Debe ser IPv4 válida |
| `device_type` | string | No, default `""` | Sí | Texto libre, sin enum observado |
| `location` | string | No, default `""` | Sí | Texto libre |
| `notes` | string | No, default `""` | Sí | Texto libre |

Los campos no reconocidos del request se rechazan. La respuesta serializa los seis campos, incluido `id`.

## Operación: listar dispositivos

- **Método y ruta:** `GET /api/v1/tools/inventory/devices`
- **Propósito:** devolver todos los dispositivos almacenados, ordenados por ID descendente (`ORDER BY id DESC`).
- **Solicitud:** sin parámetros ni body.
- **Respuesta:** `200 OK`, array JSON directo, no objeto envolvente.

```json
[
  {
    "id": 1,
    "name": "Router-Casa",
    "ip_address": "192.168.1.1",
    "device_type": "Router",
    "location": "Planta baja",
    "notes": "Puerta de enlace principal"
  }
]
```

Sin registros devuelve `200 OK` con `[]`.

## Operación: crear dispositivo

- **Método y ruta:** `POST /api/v1/tools/inventory/devices`
- **Content-Type:** `application/json`.
- **Solicitud:** `name` e `ip_address` son requeridos; los otros campos se aceptan opcionalmente.

```json
{
  "name": "Router-Casa",
  "ip_address": "192.168.1.1",
  "device_type": "Router",
  "location": "Planta baja",
  "notes": "Puerta de enlace principal"
}
```

- **Respuesta:** `201 Created` con el objeto creado y el `id` asignado.

## Operación: actualizar dispositivo

- **Método y ruta:** `PUT /api/v1/tools/inventory/devices/{device_id}`
- **Content-Type:** `application/json`.
- **Solicitud:** `device_id` es entero de ruta. El cuerpo usa `DeviceInput`: `name` e `ip_address` siguen siendo requeridos; `device_type`, `location` y `notes` son opcionales y sus defaults son `""`.
- **Semántica observada:** los valores omitidos para campos opcionales se envían al dominio como cadena vacía y reemplazan el valor previo; no se conservan automáticamente.
- **Respuesta:** `200 OK` con el objeto actualizado.

```json
{
  "name": "Router-Casa-Actualizado",
  "ip_address": "192.168.1.2"
}
```

## Operación: eliminar dispositivo

- **Método y ruta:** `DELETE /api/v1/tools/inventory/devices/{device_id}`
- **Solicitud:** sin body; `device_id` entero en la ruta.
- **Respuesta:** `204 No Content`, sin cuerpo cuando se elimina correctamente.

## Errores

Las respuestas usan el sobre global `{ "error": "<código>", "detail": "<mensaje>" }`.

| HTTP | Código `error` | Condición observada |
|---|---|---|
| `422` | `invalid_name` | `name` está presente pero vacío o solo contiene espacios |
| `422` | `invalid_ip` | `ip_address` no es una IPv4 válida |
| `422` | `not_found` | ID inexistente en PUT o DELETE; `DomainError` pasa por `domain_error_handler` |
| `422` | `missing_field` | Falta un campo requerido por `DeviceInput`, por ejemplo `name` o `ip_address` |
| `422` | `unknown_field` | El cuerpo incluye campos extra, incluido `id` |
| `422` | `invalid_type` / `invalid_value` | Tipo o valor de campo rechazado por validación Pydantic |
| `400` | `invalid_json` | Cuerpo JSON malformado en POST/PUT |
| `415` | `unsupported_media_type` | Content-Type distinto de `application/json` en POST/PUT |
| `500` | `internal_error` | Error inesperado; detalle público genérico |

El `not_found` de un dispositivo tiene HTTP 422 por ser `DomainError`; un path que no corresponde a una ruta API puede producir el 404 HTTP habitual y no es el mismo caso.

## Persistencia y pruebas de contrato

- La API obtiene el repositorio mediante `get_inventory_repo()`; el repositorio por defecto usa SQLite en `netops.db` relativo al directorio de trabajo.
- Los tests sustituyen la dependencia por `SQLiteInventoryRepository(db_path=":memory:")`.
- La respuesta de listado es array directo; las rutas de creación y actualización devuelven un dispositivo, no un objeto con clave `device`.
- Ver pruebas estáticas y casos implementados en [test-strategy.md](test-strategy.md).

## Discrepancias y pendientes

- El documento previo describía la lista como `{ "devices": [...] }`, orden ascendente, actualización parcial que conserva omitidos y `404 not_found`; ninguno coincide con el código actual.
- `netops.db` aparece rastreado por Git y `.gitignore` no contiene una regla para ignorarlo; la limpieza del repositorio requiere autorización aparte.
- El catálogo aún marca la herramienta como pendiente aunque la ruta, archivos frontend y tests existen; reconciliar su estado es una tarea documental separada.
