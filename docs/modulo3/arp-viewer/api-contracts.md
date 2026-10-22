# Contrato de API — Visor de caché ARP

> Contrato objetivo documentado a partir de la solicitud. No hay implementación observada para comparar.

## Operación: consultar caché ARP

- **Método y ruta:** `GET /api/v1/tools/arp-viewer/execute`
- **Propósito:** devolver las entradas reconocidas en la caché ARP local.
- **Content-Type:** no aplica a la solicitud GET sin body. El formato de respuesta es JSON.

### Solicitud

No se envían parámetros, query string ni cuerpo.

### Respuesta correcta

- **Estado:** `200 OK`
- **Esquema:** objeto con `entries`, una lista de asociaciones ARP.

```json
{
  "entries": [
    {
      "interface_ip": "192.168.1.33",
      "ip_address": "192.168.1.1",
      "mac_address": "aa-bb-cc-dd-ee-ff",
      "entry_type": "dynamic"
    }
  ]
}
```

| Campo | Tipo | Semántica |
|---|---|---|
| `entries` | array | Entradas parseadas de la caché local; vacío cuando la consulta correcta no encuentra asociaciones; máximo 500 elementos |
| `entries[].interface_ip` | string IPv4 | Dirección local de la sección de interfaz a la que pertenece la entrada |
| `entries[].ip_address` | string IPv4 | Dirección IP asociada a la MAC en la caché |
| `entries[].mac_address` | string | MAC normalizada como seis octetos hexadecimales separados por guiones y en minúsculas; los dos puntos de entrada se reemplazan por guiones |
| `entries[].entry_type` | string | `dynamic` o `static`; `dinámica`/`dynamic` se mapea a `dynamic`, y `estática`/`static` a `static` |

La respuesta refleja una lectura puntual de la caché; no garantiza que la asociación siga vigente al recibirla el cliente. Si la consulta se completa correctamente pero no hay entradas, responde `200 OK` con `{ "entries": [] }`. El parser devuelve como máximo 500 entradas; el criterio de selección si la salida contiene más de 500 queda pendiente.

### Errores

El dominio representa un fallo del comando o timeout mediante `DomainError` con código `execution_failed`; el handler global lo traduce a HTTP `422`. Si los cinco permisos del semáforo están ocupados, la API responde HTTP `429` con código `too_many_requests`. Una salida que no puede parsearse no fue incluida explícitamente en el mapeo de `execution_failed` y requiere definición. No se asume que DEC-012, definido para el Módulo 1, se aplique automáticamente.

| HTTP | Código `error` | Cuándo ocurre | Estado |
|---|---|---|---|
| `422` | `execution_failed` | El comando falla o supera el timeout de 10 segundos; el dominio lanza `DomainError` y el handler global lo traduce | Aprobado |
| `429` | `too_many_requests` | No hay permiso disponible en el semáforo de cinco operaciones | Aprobado |
| Pendiente | Pendiente | La salida del comando no puede interpretarse | Por decidir |

## Compatibilidad y verificación

- **OpenAPI:** endpoint objetivo; no existe implementación observada en esta auditoría documental.
- **Pruebas de contrato:** pendientes de implementar.
- **Cambios incompatibles o pendientes:** política ante salida no parseable, selección/orden cuando se supera el límite de 500 y requisitos operativos para garantizar el alcance global del semáforo.
