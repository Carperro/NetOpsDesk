# Contrato de API — Comparador de configuraciones

> Contrato objetivo de la herramienta 23, pendiente de implementación e integración.

## Operación: comparar configuraciones

- **Método y ruta:** `POST /api/v1/tools/config-comparator/compare`
- **Propósito:** comparar dos textos de configuración y devolver un diff unificado.
- **Content-Type:** `application/json`.

### Solicitud

```json
{
  "config_a": "hostname Router1\ninterface Gi0/1\n ip address 192.168.1.1 255.255.255.0",
  "config_b": "hostname Router1\ninterface Gi0/1\n ip address 192.168.1.2 255.255.255.0"
}
```

| Campo | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| `config_a` | string | Sí | Texto de la configuración original; máximo 50.000 caracteres, aplicado por el modelo Pydantic. |
| `config_b` | string | Sí | Texto de la configuración nueva; máximo 50.000 caracteres, aplicado por el modelo Pydantic. |

Al menos uno de los dos strings debe tener contenido. El tratamiento de strings vacíos en sentido semántico (por ejemplo, solo espacios) está pendiente de definición.

### Respuesta correcta

- **Estado:** HTTP `200 OK` para una solicitud válida.
- **Esquema:** objeto con `diff_lines` (array de strings) y `has_changes` (booleano).

```json
{
  "diff_lines": [
    "--- Config A",
    "+++ Config B",
    "@@ -1,3 +1,3 @@",
    " hostname Router1",
    " interface Gi0/1",
    "- ip address 192.168.1.1 255.255.255.0",
    "+ ip address 192.168.1.2 255.255.255.0"
  ],
  "has_changes": true
}
```

`diff_lines` contiene las líneas de `difflib.unified_diff` con `fromfile="Config A"`, `tofile="Config B"` y `lineterm=""`, en el orden producido. Los elementos se devuelven sin saltos de línea finales agregados por el generador. Cuando los textos son iguales, `has_changes` es `false` y `diff_lines` está vacío.

### Errores

| HTTP | Código `error` | Cuándo ocurre | `detail`/mensaje esperado |
|---|---|---|---|
| 422 | `empty_configs` | Ambos textos están vacíos; el dominio lanza `DomainError` | Mensaje pertinente en español indicando que al menos una configuración debe tener contenido. |
| 429 | `too_many_requests` | El semáforo `asyncio.Semaphore(5)` está agotado | Mensaje pertinente en español indicando que se alcanzó el límite de solicitudes concurrentes. |

La validación Pydantic también rechaza cualquier campo de configuración que supere 50.000 caracteres. El código y el detalle de esa validación deben seguir el manejo común de solicitudes inválidas aplicable al Módulo 5.

## Concurrencia

La operación se procesa bajo `asyncio.Semaphore(5)`. Si no hay permisos disponibles, la API rechaza la solicitud con HTTP `429` y código `too_many_requests`. El alcance del límite entre procesos no está definido aquí.

## Compatibilidad y verificación

- **OpenAPI:** operación POST JSON con dos strings y respuesta JSON que contiene `diff_lines` y `has_changes`.
- **Pruebas de contrato:** pendientes de implementación; deben comprobar el diff de entradas distintas e idénticas, un lado vacío, `empty_configs`, el límite de 50.000 caracteres y `too_many_requests`.
- **Cambios incompatibles o pendientes:** tratamiento de strings compuestos solo por espacios y alcance del semáforo entre procesos. El detalle/código específico para el error de longitud depende del manejo común de validación del Módulo 5.
