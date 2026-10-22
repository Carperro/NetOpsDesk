# Contrato de API — Asistente de resolución de problemas

> Contrato objetivo de la herramienta 22, pendiente de implementación e integración.

## Operación: consultar síntoma

- **Método y ruta:** `GET /api/v1/tools/troubleshooter/symptoms/{symptom_id}`
- **Propósito:** devolver causas posibles y pasos de solución para un síntoma conocido.
- **Content-Type:** no aplica a la solicitud GET sin cuerpo. El formato de respuesta es JSON.

### Solicitud

No lleva cuerpo ni parámetros de consulta. El único dato es el parámetro de ruta `symptom_id`.

| Parámetro | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| `symptom_id` | string | Sí | Identificador del síntoma estático. Valores mínimos: `sin_internet`, `internet_lento`, `dns_falla`. |

### Respuesta correcta

- **Estado:** HTTP `200 OK` para un identificador conocido.
- **Esquema:** objeto con `symptom_id`, `symptom_name` y `causes`. Cada elemento de `causes` contiene el título `cause` y una lista ordenada de strings `steps`.

```json
{
  "symptom_id": "sin_internet",
  "symptom_name": "Sin acceso a internet",
  "causes": [
    {
      "cause": "Conexión local interrumpida",
      "steps": ["Verificar el enlace físico o el estado de Wi-Fi"]
    },
    {
      "cause": "Configuración IP o gateway incorrectos",
      "steps": ["Revisar la configuración IP y la puerta de enlace asignada"]
    },
    {
      "cause": "Falla en el equipo de acceso o en el proveedor",
      "steps": ["Comprobar si otros dispositivos de la misma red tienen conectividad"]
    }
  ]
}
```

Los textos del ejemplo son ilustrativos; el contenido definitivo de causas y pasos debe mantenerse en el catálogo del dominio. El catálogo debe incluir como mínimo tres causas por síntoma.

### Errores

| HTTP | Código `error` | Cuándo ocurre | `detail`/mensaje esperado |
|---|---|---|---|
| 422 | `invalid_symptom` | El dominio no encuentra el `symptom_id` en `SYMPTOM_DATABASE`; `DomainError` se traduce mediante el handler global | Mensaje pertinente en español indicando que el síntoma no es válido o no está disponible. |
| 429 | `too_many_requests` | El semáforo `asyncio.Semaphore(5)` está agotado | Mensaje pertinente en español indicando que se alcanzó el límite de solicitudes concurrentes. |

Los errores deben usar el sobre JSON común aplicable al Módulo 5 y no exponer detalles internos.

## Concurrencia

La operación se procesa bajo `asyncio.Semaphore(5)`. Si no hay permisos disponibles, la API rechaza la solicitud con HTTP `429` y código `too_many_requests`. El semáforo asyncio limita dentro de su proceso/event loop; la coordinación entre varios workers no está definida aquí.

## Compatibilidad y verificación

- **OpenAPI:** operación GET con parámetro de ruta y sin cuerpo; respuesta JSON con causas y pasos.
- **Pruebas de contrato:** pendientes de implementación; deben comprobar identificadores conocidos, forma de respuesta, orden de causas/pasos, HTTP 422 `invalid_symptom` y HTTP 429 `too_many_requests`.
- **Cambios incompatibles o pendientes:** contenido definitivo del catálogo y política de coordinación del semáforo entre procesos.
