# Contrato de API — Catálogo de puertos y protocolos

> Contrato objetivo de la herramienta 19, pendiente de implementación e integración.

## Operación: buscar en el catálogo

- **Método y ruta:** `GET /api/v1/tools/port-catalog/search?query={texto}`
- **Propósito:** buscar registros por número de puerto o nombre de servicio; devolver todos cuando `query` está vacío.
- **Content-Type:** no se envía cuerpo. La consulta se transmite como parámetro URL codificado.

### Solicitud

Ejemplo:

```http
GET /api/v1/tools/port-catalog/search?query=http
```

| Campo | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| `query` | string | No | Texto para buscar por puerto o servicio; comparación sin distinguir mayúsculas y con coincidencia parcial. Si se omite o está vacío, se solicita el catálogo completo. |

### Respuesta correcta

- **Estado:** HTTP `200 OK`.
- **Esquema:** objeto con el array `ports`; cada registro contiene puerto, protocolo, servicio y descripción.

```json
{
  "ports": [
    {
      "port": 80,
      "protocol": "TCP",
      "service": "HTTP",
      "description": "Hypertext Transfer Protocol (World Wide Web)"
    }
  ]
}
```

| Campo | Tipo | Semántica |
|---|---|---|
| `ports` | array | Registros coincidentes; puede estar vacío si la búsqueda no encuentra resultados. |
| `ports[].port` | integer | Número de puerto del registro local. |
| `ports[].protocol` | string | Protocolo asociado, `TCP` o `UDP`. |
| `ports[].service` | string | Nombre del servicio. |
| `ports[].description` | string | Descripción legible del uso habitual. |

La búsqueda normaliza el texto de `query` mediante `.strip().lower()`. Si el resultado está vacío —incluido un valor que solo contiene espacios—, devuelve el catálogo completo. La normalización y la comparación no distinguen mayúsculas ni espacios exteriores.

### Errores

La herramienta no genera `DomainError`. Una búsqueda sin coincidencias es un resultado correcto: HTTP `200 OK` con `{"ports": []}`. Los errores de ruta o método no admitidos conservan el comportamiento HTTP de la aplicación.

| HTTP | Código `error` | Cuándo ocurre | `detail`/mensaje esperado |
|---|---|---|---|
| 429 | `too_many_requests` | Los cinco permisos del semáforo están ocupados; la solicitud se rechaza sin esperar. | Mensaje en español que indique que se alcanzó el límite de consultas concurrentes. |

## Concurrencia

La búsqueda se ejecuta bajo `asyncio.Semaphore(5)`. Si no hay permiso disponible, la solicitud se rechaza sin esperar con HTTP `429` y código `too_many_requests`. El semáforo es local al proceso/event loop; no coordina varios workers.

## Compatibilidad y verificación

- **OpenAPI:** operación GET sin cuerpo y con el parámetro opcional `query`.
- **Pruebas de contrato:** pendientes; deben comprobar respuesta completa con consulta vacía, coincidencias parciales e insensibles a mayúsculas, query numérica, lista vacía y forma de cada registro.
- **Cambios incompatibles o pendientes:** definir la semántica de subcadena para números, el orden de resultados y el alcance del semáforo al operar con varios workers; formalizar el contrato transversal de errores del Módulo 4.
