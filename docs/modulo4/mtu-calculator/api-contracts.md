# Contrato de API — Calculadora MTU y fragmentación

> Contrato objetivo de la herramienta 20, pendiente de implementación.

## Operación: calcular espacio de datos según MTU

- **Método y ruta:** `POST /api/v1/tools/mtu-calculator/calculate`
- **Propósito:** calcular el espacio disponible después de las cabeceras de IP, transporte y túnel seleccionadas.
- **Content-Type:** `application/json`.

### Solicitud

```json
{
  "mtu": 1500,
  "ip_version": "ipv4",
  "transport": "tcp",
  "tunnel": "none"
}
```

| Campo | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| `mtu` | integer | No | Default `1500`; mínimo `68`; máximo `9000`. Es el máximo de bytes del paquete IP que admite el enlace (p. ej., MTU Ethernet 1500; no incluye la cabecera Ethernet). |
| `ip_version` | string | Sí | `ipv4` o `ipv6`. |
| `transport` | string | Sí | `tcp` o `udp`. |
| `tunnel` | string | Sí | `none`, `gre`, `ipsec` o `wireguard`. |

### Respuesta correcta

- **Estado:** HTTP `200 OK` para una solicitud válida.
- **Esquema:** objeto con tamaños en bytes, espacio de datos y array de advertencias.

Ejemplo ilustrativo solo para IPv4/TCP sin túnel, con cabeceras fijas IPv4 y TCP:

```json
{
  "mtu": 1500,
  "ip_version": "ipv4",
  "transport": "tcp",
  "tunnel": "none",
  "mss": 1460,
  "ip_header_size": 20,
  "transport_header_size": 20,
  "tunnel_header_size": 0,
  "warnings": []
}
```

| Campo | Tipo | Semántica |
|---|---|---|
| `mtu` | integer | MTU usado en el cálculo, con default aplicado. |
| `ip_version` | string | Versión IP seleccionada. |
| `transport` | string | Transporte seleccionado. |
| `tunnel` | string | Túnel seleccionado. |
| `mss` | integer | Payload máximo de datos: MSS TCP si `transport` es TCP; cantidad máxima de datos UDP si es UDP. Se conserva el nombre del campo por compatibilidad contractual. Nunca es negativo: se devuelve `0` si el total de cabeceras supera el MTU. |
| `ip_header_size` | integer | Tamaño IP aplicado, en bytes. |
| `transport_header_size` | integer | Tamaño de cabecera de transporte aplicado, en bytes. |
| `tunnel_header_size` | integer | Overhead fijo del perfil seleccionado, en bytes: `none` 0, `gre` 24, `ipsec` 60, `wireguard` 60. Los perfiles de túnel usan cabecera IP exterior IPv4. |
| `warnings` | array de strings | Códigos estables de advertencia; puede estar vacío. La interfaz muestra sus mensajes en español. |

El cálculo es `max(0, mtu - ip_header_size - transport_header_size - tunnel_header_size)`. `ip_header_size` corresponde a la cabecera IP interior: IPv4 20 bytes o IPv6 40 bytes; la cabecera de transporte base es TCP 20 bytes o UDP 8 bytes. El overhead de túnel es adicional e incluye la cabecera IP exterior IPv4.

| Túnel | `tunnel_header_size` | Perfil fijado |
|---|---:|---|
| `none` | 0 | Sin encapsulación. |
| `gre` | 24 | IPv4 exterior 20 + cabecera GRE base 4; sin checksum/opciones GRE adicionales. |
| `ipsec` | 60 | IPv4 exterior 20 + overhead fijo ESP/Auth 40. |
| `wireguard` | 60 | IPv4 exterior 20 + UDP 8 + WireGuard 32. |

Si el tamaño acumulado de cabeceras es mayor que `mtu`, `mss` vale `0` y `warnings` incluye `packet_too_small`. Si `mtu < 576`, `warnings` incluye `mtu_below_minimum`; ambos códigos pueden aparecer juntos. El umbral 576 es la referencia IPv4 elegida para esta advertencia, no el límite inferior de entrada, que es 68.

### Errores

La validación de request rechaza MTU menor que 68, mayor que 9000 o fuera del tipo/rango permitido; el código HTTP específico para errores de entrada aún debe alinearse con el contrato común del Módulo 4. Los errores de ruta o método no admitidos conservan el comportamiento HTTP de la aplicación.

## Concurrencia

La operación se procesa bajo `asyncio.Semaphore(5)`. La política de saturación (espera o respuesta HTTP `429`) y el alcance entre varios workers quedan pendientes.

## Compatibilidad y verificación

- **OpenAPI:** POST JSON con MTU opcional y tres opciones enumeradas requeridas; la respuesta contiene los campos listados.
- **Pruebas de contrato:** pendientes de implementación; deben verificar defaults, límites 68/9000, enums, tamaños de cabecera, perfiles de túnel, códigos de advertencia y payload cero ante cabeceras mayores al MTU.
- **Cambios incompatibles o pendientes:** decidir si IPv6 debe generar una advertencia adicional para MTU inferior a 1280; definir el código HTTP para entrada inválida y la política de saturación/workers.
