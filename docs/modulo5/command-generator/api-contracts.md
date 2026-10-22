# Contrato de API — Generador de comandos

> Contrato objetivo aprobado para la herramienta 24; pendiente de implementación y verificación OpenAPI.

## Operación: generar comando

- **Método y ruta:** `POST /api/v1/tools/command-generator/generate`
- **Propósito:** generar un comando como texto y explicar su uso y parámetros, sin ejecutarlo.
- **Content-Type:** `application/json`.

### Solicitud

```json
{
  "command_type": "ping",
  "target": "8.8.8.8",
  "options": ["-t"]
}
```

| Campo | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| `command_type` | string | Sí | Whitelist: `ping`, `tracert`, `ipconfig`, `netstat`, `nslookup`. Valor fuera de la lista: HTTP 422, `invalid_command_type`. |
| `target` | string | Según comando | Obligatorio para `ping`, `tracert` y `nslookup`; debe ser IP o dominio válido. Ausente/vacío: HTTP 422, `missing_target`. Formato inválido: HTTP 422, `invalid_target`. Para `ipconfig` y `netstat` es opcional y puede ser vacío. |
| `options` | array de strings | Sí | Solo permite opciones de la whitelist correspondiente. Opción no permitida: HTTP 422, `invalid_option`. Si está presente, una lista vacía es válida cuando el comando no ofrece opciones. |

### Whitelist por comando

| Tipo | Opciones permitidas | `requires_admin` |
|---|---|---|
| `ping` | `-t`, `-a` | Siempre `false` |
| `tracert` | `-d` | Siempre `false` |
| `nslookup` | Ninguna | Siempre `false` |
| `ipconfig` | `/all`, `/flushdns`, `/release`, `/renew` | `true` si se selecciona `/flushdns`, `/release` o `/renew`; en otro caso `false` |
| `netstat` | `-a`, `-n`, `-b` | `true` si se selecciona `-b`; en otro caso `false` |

### Respuesta correcta

- **Estado:** HTTP `200 OK` para una solicitud válida.
- **Esquema:** objeto con `command` (string), `explanation` (string) y `requires_admin` (boolean).

```json
{
  "command": "ping -t 8.8.8.8",
  "explanation": "Envía solicitudes de eco ICMP al destino indicado de forma continua (-t).",
  "requires_admin": false
}
```

El ejemplo ilustra la forma de la respuesta. La redacción de la explicación debe describir el comando y cada opción usada. El orden de las opciones recibidas se conserva al armar el string. La aplicación devuelve el comando para copiar; no lo ejecuta.

### Errores

| HTTP | Código `error` | Cuándo ocurre |
|---|---|---|
| 422 | `invalid_command_type` | `command_type` no pertenece a la whitelist. |
| 422 | `missing_target` | Falta el objetivo requerido para `ping`, `tracert` o `nslookup`. |
| 422 | `invalid_target` | El objetivo requerido no es una dirección IP ni un dominio válido. |
| 422 | `invalid_option` | Una opción no pertenece a la whitelist del comando seleccionado. |
| 429 | `too_many_requests` | Los cinco permisos del semáforo están ocupados. |

Los errores deben incluir mensajes en español y seguir el sobre común HTTP aplicable al Módulo 5. La política transversal de dicho módulo no está especificada en este contrato.

### Concurrencia

La operación usa `asyncio.Semaphore(5)`. Si no hay permisos disponibles, responde HTTP `429` con código `too_many_requests`. El límite es el del semáforo del proceso/event loop; coordinación entre varios procesos no está definida.

## Compatibilidad y verificación

- **OpenAPI:** operación POST JSON con request de tipo, objetivo y opciones, y respuesta `{ "command": "...", "explanation": "...", "requires_admin": false }`. Pendiente de verificar al implementar.
- **Pruebas de contrato:** pendientes de implementación; deben cubrir cada whitelist, objetivos requeridos y opcionales, los cuatro errores 422, respuesta correcta, matriz de `requires_admin` y saturación 429.
- **Cambios incompatibles o pendientes:** no hay campos ni códigos de error pendientes en el alcance aprobado. La semántica general del sobre de errores debe alinearse con el contrato común del Módulo 5.