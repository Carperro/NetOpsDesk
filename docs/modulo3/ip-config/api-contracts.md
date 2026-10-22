# Contrato de API — Asistente de configuración IP

> Especificación documental aprobada para la ruta, las acciones, los campos y los errores 422. No describe una implementación existente. La respuesta exitosa permanece pendiente de formalización.

## Operación: generar comandos de configuración

- **Método y ruta:** `POST /api/v1/tools/ip-config/execute`
- **Propósito:** validar la acción solicitada y devolver un comando de Windows en texto plano con una explicación. El servidor no ejecuta el comando.
- **Content-Type:** se espera JSON; estado y sobre para tipo no admitido pendientes del contrato común del Módulo 3.

### Solicitud

```json
{
  "action": "set_static",
  "interface_name": "Wi-Fi",
  "ip": "192.168.1.100",
  "mask": "255.255.255.0",
  "gateway": "192.168.1.1"
}
```

| Campo | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| `action` | string | Sí | `renew_dhcp`, `set_dhcp`, `set_static` o `set_dns` |
| `interface_name` | string | Sí para todas las acciones | Nombre de interfaz. Se rechazan comillas dobles (`"`), backticks y caracteres de control |
| `ip` | string IPv4 | Sí para `set_static` | Dirección que se configuraría |
| `mask` | string IPv4 | Sí para `set_static` | Máscara que se configuraría |
| `gateway` | string IPv4 | Sí para `set_static` | Puerta de enlace que se configuraría |
| `dns_ip` | string IPv4 | Sí para `set_dns` | Servidor DNS que se configuraría con el comando IPv4 `netsh interface ip` |

Los campos requeridos dependen de `action`: además de `interface_name`, `set_static` requiere `ip`, `mask` y `gateway`; `set_dns` requiere `dns_ip`; `renew_dhcp` y `set_dhcp` no requieren campos adicionales. La configuración DNS se limita a una dirección por operación. No se han aprobado dirección IPv6 ni ejecución del comando. La política para campos adicionales no está definida.

### Comandos generados

El dominio genera estas cadenas, sustituyendo los marcadores por valores validados:

| Acción | Comando |
|---|---|
| `renew_dhcp` | `ipconfig /renew "{interface_name}"` |
| `set_dhcp` | `netsh interface ip set address name="{interface_name}" source=dhcp` |
| `set_static` | `netsh interface ip set address name="{interface_name}" static {ip} {mask} {gateway}` |
| `set_dns` | `netsh interface ip set dns name="{interface_name}" static {dns_ip}` |

Las comillas que rodean `interface_name` pertenecen a la plantilla del comando; el valor no puede contener comillas dobles, backticks ni controles.

### Respuesta correcta

- **Estado:** pendiente de confirmar; se propone `200` para una generación válida.
- **Esquema propuesto, aún no aprobado:**

```json
{
  "action": "set_static",
  "command": "netsh interface ip set address name=\"Wi-Fi\" static 192.168.1.100 255.255.255.0 192.168.1.1",
  "explanation": "Configura la interfaz Wi-Fi con la dirección IPv4, máscara y puerta de enlace indicadas."
}
```

`command` y `explanation` son una propuesta de respuesta mínima derivada del resultado solicitado, no un contrato aprobado. La respuesta nunca representa que el comando haya sido ejecutado.

### Errores

| HTTP | Código `error` | Cuándo ocurre | `detail`/mensaje esperado |
|---|---|---|---|
| `422` | `invalid_action` | `action` no es una de las cuatro acciones admitidas | Mensaje pertinente en español |
| `422` | `missing_fields` | Falta `interface_name` o un campo requerido por la acción | Mensaje pertinente en español |
| `422` | `invalid_ip_format` | `ip`, `mask`, `gateway` o `dns_ip` no tiene el formato IP requerido | Mensaje pertinente en español |
| `422` | `invalid_interface_name` | `interface_name` contiene comillas dobles, backticks o caracteres de control | Mensaje pertinente en español |

Los códigos anteriores se responden con HTTP `422`. El sobre JSON común y los estados para otros errores deben alinearse con el contrato vigente del Módulo 3; no se asume automáticamente que DEC-012 del Módulo 1 aplique aquí.

## Compatibilidad y verificación

- **OpenAPI:** no hay implementación ni esquema observado para esta herramienta.
- **Pruebas de contrato:** pendientes de implementación.
- **Cambios incompatibles o pendientes:** aprobar respuesta exitosa, tratamiento de campos extra y estados/códigos para errores distintos de los cuatro 422 definidos.
