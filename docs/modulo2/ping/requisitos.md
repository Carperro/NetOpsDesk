# Requisitos — Ping

> Documento de diseño de la herramienta 6. No describe comportamiento implementado: Ping sigue pendiente de desarrollo e integración frontend según el catálogo.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 2, herramienta 6.
- **Propósito:** medir latencia y pérdida de paquetes ICMP hacia un host y presentar un diagnóstico acotado.
- **Incluye:** entrada de IPv4, IPv6 o nombre de host; resolución de la dirección efectivamente probada; tiempos de respuesta individuales y estadísticas agregadas.
- **No incluye en v1:** escaneo de rangos, puertos TCP, traceroute, ejecución de comandos arbitrarios, selección de parámetros del sistema operativo ni diagnóstico de rutas.
- **Familias/protocolos admitidos:** IPv4 e IPv6 ICMP Echo, mediante el ejecutable `ping.exe` de Windows; nombres de host conforme a RFC 1123.

La pertenencia de Ping al MVP está aprobada por DEC-011. La decisión histórica DEC-003 excluía herramientas de diagnóstico del sistema operativo, pero DEC-011 la sustituye en ese punto. La inclusión en el MVP no equivale a autorización para exponer la aplicación por LAN ni define autenticación.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| PING-F-001 | Ejecutar una prueba ICMP a un host | `host` válido: IPv4, IPv6 o hostname RFC 1123 | Diagnóstico del host probado y dirección IP resuelta | APROBADO por la instrucción del usuario; pendiente de implementación |
| PING-F-002 | Limitar la cantidad de solicitudes Echo | `count` entero; default 4, mínimo 1, máximo 10 | Se envían como máximo 10 solicitudes por operación | APROBADO por la instrucción del usuario |
| PING-F-003 | Informar el resultado agregado | Ejecución terminada | IP resuelta, enviados/recibidos, pérdida porcentual y mínimo, máximo y promedio en milisegundos | APROBADO por la instrucción del usuario; semántica de ausencia de respuestas detallada abajo |
| PING-F-004 | Informar respuestas individuales | Una o más respuestas Echo recibidas | Lista ordenada de tiempos individuales; `seq` es un ordinal consecutivo asignado por el parser (1..N), sin representar ni inferir el índice del intento ICMP | APROBADO por el usuario; pendiente de implementación |
| PING-F-005 | Tratar falta de respuestas como resultado de diagnóstico | La ejecución termina y no llega ninguna respuesta Echo | Pérdida de 100%; lista vacía y estadísticas de latencia nulas; no se presenta como error de conectividad del servidor | APROBADO por el usuario |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| PING-NF-001 | Validación y Command Injection | Validar `host` antes de invocar el sistema operativo. Rechazar controles, espacios, CR/LF, NUL, `&`, `\|`, `;`, `>`, `<`, backticks, prefijos de opción y cualquier forma que no sea una IP o hostname admitido. Usar validación sintáctica estricta: expresiones regulares para las formas IPv4/IPv6 y hostname, además de parseo estándar de la IP para verificar su semántica. | Valores de prueba hostiles se rechazan en dominio y API y no llegan al runner. | APROBADO como requisito; patrones exactos y política de nombres pendientes de concretar |
| PING-NF-002 | Ejecución de procesos | Invocar únicamente `ping.exe`, con argumentos separados, `shell=False` y sin concatenar una cadena de comando. | La prueba del adaptador verifica lista de argumentos, host como argumento final y ausencia de shell. | APROBADO como requisito de diseño |
| PING-NF-003 | Tiempo | Límite duro de 15 segundos por proceso, incluyendo resolución realizada por `ping.exe`; el adaptador aplica un timeout del proceso además del timeout por respuesta `-w 2000`. | El proceso termina o se cancela al alcanzar el límite; la API responde HTTP 504 con `ping_timeout`; no queda un subproceso huérfano. | APROBADO por el usuario |
| PING-NF-004 | Privilegios | La operación normal no solicita elevación ni requiere ejecutar NetOps Desk como administrador en Windows para emitir ping ICMP. La política de firewall local o de destino puede bloquear respuestas. | Ejecución con la cuenta estándar del servicio; ningún paso de elevación. | APROBADO por la instrucción del usuario; verificar en los entornos objetivo |
| PING-NF-005 | Localización | No depender de frases exactas en inglés o español del sistema operativo. Extraer duraciones mediante patrones numéricos alrededor de `ms` y reconocer la estructura de respuesta por datos, no por textos traducidos. | Fixtures en inglés y español producen los mismos datos normalizados. | APROBADO como criterio; compatibilidad real de formatos pendiente de prueba |
| PING-NF-006 | Recursos | `count` no supera 10; la duración total del proceso no supera 15 segundos; como máximo se ejecutan 5 pings simultáneos globalmente. No aceptar listas de hosts, intervalos ni parámetros de ping arbitrarios. | Un `asyncio.Semaphore(5)` en API limita concurrencia; la aplicación se despliega con un único worker Uvicorn para que el límite sea global. El exceso recibe HTTP 429. | APROBADO por el usuario |
| PING-NF-007 | Privacidad y seguridad operativa | No registrar salida cruda de `ping.exe`, ni reflejarla en errores públicos. No persistir hosts probados. La autorización, limitación de frecuencia y exposición fuera del equipo requieren decisión previa. | Logs y respuestas contienen códigos y detalles seguros, sin stdout/stderr ni datos innecesarios. | Privacidad aprobada como directiva de diseño; política de acceso pendiente |

## Criterios de aceptación

- `host="8.8.8.8"`, sin `count`, usa 4 solicitudes; se aceptan los límites 1 y 10 y se rechazan 0 y 11.
- Un host IPv4, IPv6 o hostname permitido llega al proceso solo después de validarse; una entrada con controles, espacios, metacaracteres de shell o sintaxis de opción se rechaza.
- El resultado de una operación completada contiene host original, dirección IP efectivamente probada, cantidades enviadas/recibidas, porcentaje de pérdida y latencias individuales/agregadas.
- La pérdida se calcula como `(packets_sent - packets_received) / packets_sent * 100`. Las latencias agregadas se calculan solo sobre respuestas recibidas; si no hay respuestas, min/avg/max son `null`.
- `seq` identifica el ordinal consecutivo de cada respuesta exitosa (`1..N`), sin huecos. No representa el número de intento ICMP y el parser no intenta adivinar qué paquete se perdió.
- Un RTT presentado por Windows como `<1ms` se convierte a `0.0` (número), nunca a una cadena.
- La pérdida total de paquetes devuelve HTTP 200 con `packets_received: 0`, `packet_loss_percent: 100`, `min_ms`, `max_ms` y `avg_ms` en `null`, y `responses: []`.
- Host/count inválidos devuelven HTTP 422 (`invalid_host`/`invalid_count`); timeout total del subprocess devuelve HTTP 504 (`ping_timeout`); fallo de ejecución del binario devuelve HTTP 500 (`execution_failed`).
- La sexta solicitud simultánea recibe HTTP 429 cuando los cinco permisos del semáforo están ocupados; Uvicorn corre con un único worker.
- El proceso no excede 15 segundos, no usa shell y sus argumentos no se construyen mediante interpolación de comando.
- Los mensajes destinados a usuario están en español; los detalles internos de Windows no se exponen.

## Fuentes y pendientes

- **Decisiones aplicables:** [DEC-011 — alcance del MVP](../../fundacional/decision-log.md#dec-011--alcance-del-mvp); las exclusiones históricas incompatibles de DEC-003 quedan sustituidas por DEC-011.
- **Fuentes técnicas:** [RFC 1123, sección 2.1](https://www.rfc-editor.org/rfc/rfc1123.html#section-2.1); [documentación de `ping` de Microsoft](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ping), que define `/n` como cantidad de solicitudes y `/w` como espera por respuesta.
- **Pendiente de aprobación o investigación:** política de dominios absolutos con punto final e IDN; política de frecuencia y de acceso antes de exposición por LAN. Las decisiones de `seq`, `<1ms`, estados HTTP y concurrencia constan en [decision-log.md](decision-log.md).
