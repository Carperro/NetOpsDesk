# Contrato de API — Información de interfaces de red

## Estado

Contrato objetivo de una herramienta pendiente de implementación e integración según el catálogo.

## Operación: listar interfaces locales

- **Método y ruta:** `GET /api/v1/tools/interfaces/execute`
- **Propósito:** devolver información de interfaces del servidor que ejecuta NetOps Desk.
- **Content-Type:** sin request body; no se requieren parámetros.

### Solicitud

No se envían parámetros ni cuerpo.

### Respuesta correcta

- **Estado:** HTTP `200 OK` cuando la consulta se completa.
- **Esquema:** objeto raíz con array `interfaces`.

```json
{
  "interfaces": [
    {
      "name": "Ethernet",
      "mac_address": "00:11:22:33:44:55",
      "ipv4": "192.168.1.50",
      "netmask": "255.255.255.0",
      "gateway": "192.168.1.1",
      "dns_servers": [
        "192.168.1.1",
        "8.8.8.8"
      ],
      "is_up": true,
      "speed_mbps": 1000
    }
  ]
}
```

| Campo | Tipo | Semántica |
|---|---|---|
| `interfaces` | array | Interfaces locales devueltas por el runner. |
| `interfaces[].name` | string | Nombre de interfaz informado por el sistema. |
| `interfaces[].mac_address` | string o null | Dirección MAC; `null` si no está disponible (por ejemplo, loopback). |
| `interfaces[].ipv4` | string o null | Dirección IPv4; `null` si no está disponible (por ejemplo, loopback). |
| `interfaces[].netmask` | string o null | Máscara de IPv4; `null` si no está disponible. |
| `interfaces[].gateway` | string o null | Gateway asociado a la interfaz; `null` si no está disponible. |
| `interfaces[].dns_servers` | array de strings | Servidores DNS asociados a la interfaz; puede ser `[]`. |
| `interfaces[].is_up` | boolean | Estado operativo de interfaz informado por psutil. |
| `interfaces[].speed_mbps` | integer | Velocidad en Mbps; `0` cuando el sistema no informa la velocidad. |

La respuesta describe la máquina servidor, no el dispositivo navegador.

### Errores

La política HTTP para fallo al consultar psutil, error inesperado o respuesta parcial no se fijó en la solicitud. Se debe definir con el contrato común del Módulo 3 antes de implementar. Los mensajes destinados a la interfaz deben estar en español y no revelar detalles internos.

## Compatibilidad y verificación

- **OpenAPI:** operación GET sin body; el modelo de salida debe reflejar exactamente los nombres y tipos aquí documentados.
- **Pruebas de contrato:** pendientes de implementación; deben comprobar respuesta vacía, una o más interfaces y campos opcionales cuando se apruebe su semántica.
- **Cambios incompatibles o pendientes:** selección entre varias IPv4/gateways de una interfaz, asociación de secciones de `ipconfig /all` a los nombres de psutil y política de errores.
