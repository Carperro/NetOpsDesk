# Contrato de API — Analizador de gateway y rutas

## Estado

Contrato objetivo para una herramienta pendiente de desarrollo e integración según el catálogo. El endpoint y la respuesta positiva siguen la especificación aprobada por el usuario; el contrato de errores queda pendiente.

## Operación: consultar configuración IPv4 local

- **Método y ruta:** `GET /api/v1/tools/route-analyzer/execute`
- **Propósito:** obtener el gateway predeterminado y las rutas IPv4 de la máquina donde corre el servidor.
- **Content-Type:** no hay request body. La política de `Accept` no se especificó.

### Solicitud

No se envían parámetros ni cuerpo.

### Respuesta correcta

- **Estado:** HTTP `200 OK` cuando ambos comandos se ejecutan y sus datos se pueden interpretar.
- **Esquema:** `default_gateway` es la dirección IPv4 del gateway identificado; `routes` contiene las rutas IPv4 encontradas.

```json
{
  "default_gateway": "192.168.1.1",
  "routes": [
    {
      "destination": "0.0.0.0",
      "netmask": "0.0.0.0",
      "gateway": "192.168.1.1",
      "interface": "192.168.1.50",
      "metric": 25
    }
  ]
}
```

| Campo | Tipo | Semántica |
|---|---|---|
| `default_gateway` | string | IPv4 del gateway predeterminado seleccionado: menor métrica entre los candidatos; si no hay métricas para compararlos, el primero en el orden de `ipconfig`. El caso sin gateway queda pendiente. |
| `routes` | array | Filas IPv4 reconocidas en `route print -4`. |
| `routes[].destination` | string | Destino de la ruta en IPv4. |
| `routes[].netmask` | string | Máscara IPv4. |
| `routes[].gateway` | string | Gateway de la fila según salida del sistema; formato on-link requiere definición. |
| `routes[].interface` | string | Dirección IPv4 de interfaz asociada. |
| `routes[].metric` | integer | Métrica numérica de la ruta. |

La respuesta describe la red local del servidor, no la del cliente HTTP.

### Errores

Si falla la ejecución de cualquiera de los comandos (incluido el timeout de 10 segundos) o no se puede parsear la salida requerida (por ejemplo, no se encuentra la tabla de rutas), se responde HTTP `500 Internal Server Error` con el código `execution_failed`. La condición es un fallo del sistema, no un error del usuario. El detalle público debe ser genérico y no exponer stdout, stderr, rutas internas ni trazas.

```json
{
  "error": "execution_failed",
  "detail": "No se pudo obtener la configuración de rutas del sistema."
}
```

La representación cuando no existe gateway y el tratamiento de una respuesta parcial requieren definición adicional. No se asume automáticamente el mapeo del contrato común del Módulo 1 para esos casos.

## Compatibilidad y verificación

- **OpenAPI:** operación GET sin body; los modelos de salida se definirán al implementar según este esquema.
- **Pruebas de contrato:** pendientes; deberán confirmar que no se requiere body y que se serializan las rutas con los cinco campos.
- **Cambios incompatibles o pendientes:** nulabilidad de `default_gateway`, rutas on-link y fallo parcial requieren decisión.
