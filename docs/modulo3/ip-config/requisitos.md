# Requisitos — Asistente de configuración IP

> Estado: especificación documental de la herramienta 12; no describe una implementación existente.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 3, herramienta 12.
- **Propósito:** generar y explicar comandos de Windows para configurar una interfaz mediante DHCP o dirección IPv4 estática.
- **Incluye:** acciones `renew_dhcp`, `set_dhcp` y `set_static`; entrega de un comando en texto plano y una explicación para que la persona decida si lo ejecuta manualmente.
- **No incluye:** ejecutar comandos en el servidor, modificar directamente la configuración de red ni solicitar que el servidor aplique cambios.
- **Familias/protocolos admitidos:** la solicitud actual especifica IPv4 para la configuración estática; no define configuración IPv6.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| IPC-F-001 | Generar una instrucción para renovar DHCP | `action=renew_dhcp` y nombre de interfaz | Comando de texto y explicación | Aprobado en el alcance de la tarea |
| IPC-F-002 | Generar una instrucción para habilitar DHCP | `action=set_dhcp` y nombre de interfaz | Comando de texto y explicación | Aprobado en el alcance de la tarea |
| IPC-F-003 | Generar una instrucción para configurar IP estática | `action=set_static`, `ip`, `mask` y `gateway` | Comando de texto y explicación | Aprobado en el alcance de la tarea |
| IPC-F-004 | Mostrar el comando generado para copiarlo | Respuesta de generación correcta | Interfaz presenta el comando y ofrece copiarlo al portapapeles | Aprobado en el alcance de la tarea |

Para `set_dhcp` y `renew_dhcp`, se requiere `interface_name`. Para `set_static`, se requieren `ip`, `mask` y `gateway`; el tratamiento de `interface_name` en esta acción no fue especificado.

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| IPC-NF-001 | Seguridad | El servidor genera texto; nunca ejecuta `subprocess` ni comandos del sistema | Ninguna ruta de generación invoca un intérprete o proceso del sistema | Aprobado |
| IPC-NF-002 | Rendimiento | La operación es generación de strings y debe ser inmediata | La generación no realiza operaciones de red o sistema operativo | Aprobado |
| IPC-NF-003 | Seguridad de entrada | Los valores insertados en el comando deben validarse y escaparse conforme a la sintaxis elegida | Entradas con metacaracteres o controles no pueden alterar la estructura del comando | Pendiente de especificar la gramática exacta |

## Criterios de aceptación

- Cada una de las tres acciones aceptadas genera el comando y una explicación pertinente en español.
- Si faltan campos requeridos para una acción o sus valores son inválidos, la API rechaza la solicitud sin generar texto ejecutable.
- La interfaz muestra el comando como texto y permite copiarlo; copiarlo no lo ejecuta.
- La aplicación no cambia la configuración de red del servidor y no inicia procesos del sistema.
- Antes de cerrar el contrato, se define si `set_static` requiere también `interface_name`, cómo se validan los parámetros y cuáles son los comandos exactos para cada acción.

## Fuentes y pendientes

- **Decisiones aplicables:** alcance aprobado en la solicitud del usuario para la herramienta 12.
- **Fuentes técnicas verificadas:** ninguna norma o referencia externa fue especificada en esta tarea.
- **Pendiente de aprobación o investigación:** formato exacto de cada comando; validación de nombres de interfaz; si `set_static` necesita nombre de interfaz; alcance de DNS previsto en el catálogo; esquema de respuesta y contrato de errores HTTP.
