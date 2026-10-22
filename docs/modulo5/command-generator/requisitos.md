# Requisitos — Generador de comandos

> Especificación aprobada para la herramienta 24. La herramienta está pendiente de implementación e integración.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 5, herramienta 24.
- **Propósito:** preparar comandos de red y explicar qué hace el comando y cada uno de sus parámetros.
- **Incluye:** seleccionar una plantilla, completar los campos aplicables y obtener un comando de texto, su explicación y el indicador de privilegios requerido.
- **No incluye:** ejecutar comandos ni producir efectos en el equipo desde la aplicación.
- **Familias/protocolos admitidos:** comandos de Windows: `ping`, `tracert`, `ipconfig`, `netstat` y `nslookup`.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| REQ-F-001 | Seleccionar el tipo de comando | `command_type` es uno de `ping`, `tracert`, `ipconfig`, `netstat` o `nslookup` | Se selecciona la plantilla correspondiente | Aprobado |
| REQ-F-002 | Recibir el objetivo cuando corresponda | `target` es requerido para `ping`, `tracert` y `nslookup`; es opcional para `ipconfig` y `netstat` | El comando incorpora el objetivo aplicable | Aprobado |
| REQ-F-003 | Recibir opciones | `options` contiene cero o más opciones permitidas para el tipo elegido | Se incorporan únicamente opciones de la whitelist de ese comando | Aprobado |
| REQ-F-004 | Generar el comando | Tipo, objetivo y opciones válidos | `command` contiene el comando preparado como string | Aprobado |
| REQ-F-005 | Explicar el comando | Comando generado | `explanation` describe qué hace el comando y cada opción o parámetro utilizado | Aprobado |
| REQ-F-006 | Indicar necesidad de privilegios | Tipo y opciones seleccionados | `requires_admin` es `true` solo cuando se selecciona una opción marcada como administrativa | Aprobado |
| REQ-F-007 | No ejecutar el comando | Solicitud válida | La aplicación devuelve y muestra texto; no ejecuta el comando | Aprobado |

### Catálogo estricto de comandos

| `command_type` | `target` | Opciones permitidas | `requires_admin` |
|---|---|---|---|
| `ping` | Requerido; IP o dominio válido | `-t`, `-a` | `false` |
| `tracert` | Requerido; IP o dominio válido | `-d` | `false` |
| `nslookup` | Requerido; IP o dominio válido | Ninguna | `false` |
| `ipconfig` | Opcional; puede ser vacío | `/all`, `/flushdns`, `/release`, `/renew` | `true` si se selecciona `/flushdns`, `/release` o `/renew`; en otro caso `false` |
| `netstat` | Opcional; puede ser vacío | `-a`, `-n`, `-b` | `true` si se selecciona `-b`; en otro caso `false` |

Las opciones no incluidas en la fila del tipo elegido se rechazan. El orden de las opciones recibidas se conserva al construir el comando.

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| REQ-NF-001 | Seguridad | Validar que los objetivos requeridos sean una IP o dominio válido antes de incorporarlos al texto | Objetivo requerido ausente produce `missing_target`; formato inválido produce `invalid_target` | Aprobado |
| REQ-NF-002 | Seguridad | Aplicar whitelist estricta tanto al tipo de comando como a sus opciones | Tipo no permitido produce `invalid_command_type`; opción no permitida para el tipo produce `invalid_option` | Aprobado |
| REQ-NF-003 | Concurrencia | La API utiliza `asyncio.Semaphore(5)` | Al agotarse los permisos, responder HTTP 429 con `too_many_requests` | Aprobado |
| REQ-NF-004 | Efectos | No ejecutar procesos ni comandos del sistema operativo | No invocar `subprocess` ni otro ejecutor | Aprobado |
| REQ-NF-005 | Presentación | Mostrar el comando como texto copiable en un `<textarea>` o `<code>` | El comando se presenta sin interpretarse como HTML | Aprobado; elemento visual a elección de la interfaz |

## Criterios de aceptación

- Cada uno de los cinco tipos admitidos genera una respuesta con `command`, `explanation` y `requires_admin`.
- `ping`, `tracert` y `nslookup` requieren un objetivo válido. `ipconfig` y `netstat` aceptan el objetivo omitido o vacío.
- Una opción ajena a la whitelist del tipo seleccionado se rechaza con HTTP 422 y `invalid_option`.
- Un tipo no permitido se rechaza con HTTP 422 y `invalid_command_type`.
- La ausencia de objetivo requerido se rechaza con HTTP 422 y `missing_target`; un objetivo requerido que no sea IP ni dominio válido se rechaza con HTTP 422 y `invalid_target`.
- La matriz de privilegios se respeta: `ipconfig` requiere administrador solo con `/flushdns`, `/release` o `/renew`; `netstat`, solo con `-b`; los demás casos son `false`.
- Al agotarse el semáforo de cinco permisos, la API responde HTTP 429 con `too_many_requests`.
- La aplicación nunca ejecuta el comando generado.

## Fuentes y pendientes

- **Decisiones aplicables:** DEC-011 — alcance del MVP en [registro global](../../fundacional/decision-log.md#dec-011--alcance-del-mvp); decisiones específicas CMD-DEC-01 a CMD-DEC-04 en [registro de decisiones](decision-log.md).
- **Fuentes técnicas verificadas:** alcance y whitelist definidos por instrucción explícita del usuario el 2026-10-20.
- **Pendiente de aprobación o investigación:** ninguno para la whitelist, errores y concurrencia aprobados. La gramática de dominio/IP debe implementarse con límites explícitos.