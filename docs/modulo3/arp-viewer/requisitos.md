# Requisitos — Visor de caché ARP

> Estado: especificación documental de la herramienta 13; describe el alcance aprobado, no una implementación existente.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 3, herramienta 13.
- **Propósito:** mostrar las asociaciones IP/MAC presentes en la caché ARP local de Windows.
- **Incluye:** consulta sin parámetros y presentación de interfaz local, IP destino, dirección MAC y tipo de entrada (dinámica o estática).
- **No incluye:** modificar la caché ARP, enviar solicitudes de red por cada entrada ni recibir destinos del usuario.
- **Familias/protocolos admitidos:** tabla ARP IPv4 (`arp -a`).

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| ARP-F-001 | Consultar la caché ARP local | Solicitud sin parámetros | Se ejecuta la consulta fija `arp -a` mediante el adaptador | Aprobado |
| ARP-F-002 | Presentar las entradas reconocidas | Salida estructurada por el dominio | Cada elemento contiene `interface_ip`, `ip_address`, `mac_address` y `entry_type` | Aprobado |
| ARP-F-003 | Asociar entradas con su interfaz | Salida contiene secciones por interfaz | Cada entrada se vincula a la IP de interfaz anunciada por Windows | Aprobado |
| ARP-F-004 | Reconocer tipos de entrada | La línea contiene una entrada ARP válida | `entry_type` es `dynamic` o `static` | Aprobado; cobertura de idiomas por definir |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| ARP-NF-001 | Recursos | El comando tiene un timeout de 10 segundos | Si vence, se termina la operación y no se bloquea indefinidamente | Aprobado |
| ARP-NF-002 | Concurrencia | La API usa `asyncio.Semaphore(5)` | No hay más de cinco operaciones simultáneas dentro del alcance del semáforo | Aprobado; alcance entre workers pendiente |
| ARP-NF-003 | Seguridad | Ejecutar el comando fijo con argumentos separados y `shell=False`; no incorporar entrada del cliente | No existe un canal de inyección desde parámetros HTTP | Aprobado |
| ARP-NF-004 | Robustez | Interpretar la salida tolerando bytes no decodificables y variaciones de idioma | Decodificación con `errors="replace"` y parser que no depende de encabezados rígidos | Aprobado como objetivo; idiomas soportados por concretar |

## Criterios de aceptación

- `GET /api/v1/tools/arp-viewer/execute` no necesita body ni parámetros.
- Las entradas válidas se devuelven agrupadas por interfaz, con MAC normalizada al formato `xx-xx-xx-xx-xx-xx` y tipo `dynamic` o `static`.
- Una línea malformada o un encabezado no reconocido no se convierte en una entrada inventada ni desplaza la asociación de interfaz.
- El comando fijo no usa shell y la operación respeta el timeout de 10 segundos.
- La respuesta no afirma que una asociación esté activa ahora; refleja únicamente lo que reportó la caché consultada.

## Fuentes y pendientes

- **Decisiones aplicables:** alcance aprobado por la solicitud del usuario para la herramienta 13.
- **Fuentes técnicas verificadas:** ninguna referencia externa se especificó en esta tarea.
- **Pendiente de aprobación o investigación:** idiomas/formas de salida que se soportarán; comportamiento HTTP ante fallo o timeout del comando; política de saturación del semáforo y garantía entre varios workers; límite máximo de salida parseada; tratamiento de interfaces sin entradas.
