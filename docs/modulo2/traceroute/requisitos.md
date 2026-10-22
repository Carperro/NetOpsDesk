# Requisitos — Traceroute

> Diseño de la herramienta 7 del Módulo 2. No describe una implementación existente. El catálogo registra Traceroute como pendiente de desarrollo e integración frontend.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 2, herramienta 7.
- **Propósito:** mapear los saltos de red que responden en la ruta hacia un host destino.
- **Incluye:** recibir una dirección IPv4, IPv6 o un dominio; ejecutar `tracert.exe` en Windows; devolver la IP de destino resuelta y los saltos observados con direcciones y tiempos de respuesta.
- **No incluye en v1:** escaneo de rangos o puertos, traceroute con parámetros elegidos por el cliente, resolución DNS inversa de los routers intermedios, modificación de rutas o garantía de que todos los routers respondan.
- **Familias/protocolos admitidos:** IPv4 e IPv6 mediante `tracert.exe`; el comportamiento para dominios sigue la selección de familia de Windows salvo que una decisión posterior defina otra política.

La pertenencia de Traceroute al MVP deriva de DEC-011 y del catálogo. Esto no autoriza exposición por LAN, autenticación ni ampliación de destinos permitidos.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| TRACE-F-001 | Trazar una ruta hacia un host | `host` IPv4, IPv6 o dominio aceptado por las reglas de Ping | Host, IP de destino resuelta y lista ordenada de saltos observados | Aprobado por la instrucción del usuario; pendiente de implementación |
| TRACE-F-002 | Acotar la cantidad de saltos | `max_hops` opcional; mínimo `1`, default `15`, máximo `30` | El proceso no busca más saltos que el límite indicado | APROBADO por el usuario; pendiente de implementación |
| TRACE-F-003 | Describir cada salto | Fila de salto presente en la salida de `tracert.exe` | `hop_number`, IP o `null` y los tiempos numéricos que pudieron extraerse | APROBADO por el usuario; pendiente de implementación |
| TRACE-F-004 | Representar routers sin respuesta y probes parciales | Fila con uno o más probes agotados | El salto no se omite; si no hay respuestas usa `ip: null`, `times_ms: []`; tiempos parciales incluyen solo mediciones recibidas | APROBADO por el usuario; pendiente de implementación |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| TRACE-NF-001 | Validación y Command Injection | Validar estrictamente IPv4, IPv6 y dominios con la política de host de Ping; rechazar controles, espacios, saltos de línea, metacaracteres y argumentos de opción. La validación de UI no sustituye la de API y dominio. | Entradas inválidas no alcanzan el runner; argumentos se pasan como elementos separados, nunca como línea de shell. | Aprobado en alcance; política DNS exacta sigue pendiente en Ping |
| TRACE-NF-002 | Ejecución de procesos | Usar `tracert.exe` con argumentos fijos, `shell=False`; el cliente no puede elegir flags ni ejecutable. | La prueba del adaptador verifica vector de argumentos y ausencia de shell. | Aprobado por la instrucción del usuario |
| TRACE-NF-003 | Tiempo | Timeout duro de 30 segundos para el subprocess; al vencer se termina el proceso. | No queda proceso huérfano; la API informa el timeout según el contrato que se apruebe. | Aprobado el límite; traducción HTTP pendiente de formalización para Módulo 2 |
| TRACE-NF-004 | Memoria y salida | No retener más de 64 KiB de `stdout` por ejecución. | El runner limita la captura mientras lee; no basta con comprobar el tamaño después de materializar toda la salida. | Aprobado el límite; mecanismo de terminación por exceso propuesto |
| TRACE-NF-005 | Rendimiento | Limitar saltos a 30 y espera por respuesta a 1000 ms. El deadline global de 30 s interrumpe ejecuciones que superen ese tiempo. | Casos máximos verifican que el proceso quede acotado por el deadline global. | Aprobado por la instrucción del usuario |
| TRACE-NF-006 | Privacidad y seguridad operativa | No exponer salida cruda del proceso, rutas locales ni trazas en la respuesta pública; no persistir destinos por esta herramienta. | Errores públicos seguros y salida parseada por campos. | Principio aprobado por `AGENTS.md`; detalle operativo de Ping sirve de referencia |
| TRACE-NF-007 | Concurrencia | Máximo global de 3 ejecuciones simultáneas mediante `asyncio.Semaphore(3)`; un único worker Uvicorn. | Cuando los tres espacios estén ocupados, la solicitud adicional recibe HTTP 429; el semáforo no se replica entre workers. | APROBADO por el usuario |

## Criterios de aceptación

- `host="8.8.8.8"` y `max_hops` omitido aplica 15; se acepta como máximo 30 saltos.
- `max_hops` acepta enteros estrictos entre 1 y 30; omitido aplica 15. Valores fuera de rango o de tipo incorrecto se rechazan antes de iniciar el proceso.
- Una entrada hostil o inválida se rechaza en API/dominio y nunca se incorpora a una cadena de shell.
- La invocación usa `tracert /h <max_hops> /w 1000 /d <host>`, lista de argumentos y `shell=False`; el proceso tiene timeout total de 30 segundos.
- El parser reconoce número de salto al comienzo de la fila, direcciones IP y tiempos de respuesta; una fila sin IP y con `*` representa un salto que no respondió.
- La respuesta mantiene todos los saltos observados, ordenados por `hop_number`; no omite filas sin respuesta. Un salto sin respuestas usa `ip: null` y `times_ms: []`; si llegan una o dos mediciones, `times_ms` contiene solo esas mediciones numéricas, sin elementos `null`.
- La operación devuelve HTTP 200 si termina al llegar al destino o al alcanzar `max_hops`. Errores de entrada devuelven 422 (`invalid_host`, `invalid_max_hops`), timeout total 504 (`traceroute_timeout`), fallo de ejecución 500 (`execution_failed`) y saturación del semáforo 429 (`too_many_requests`).
- Como máximo corren tres procesos Traceroute simultáneamente en el despliegue de un solo worker; la cuarta solicitud concurrente se rechaza con HTTP 429.
- La salida estándar retenida no supera 64 KiB por ejecución; al alcanzar el límite el proceso no continúa generando salida retenida de manera ilimitada.
- Los mensajes dirigidos al usuario están en español y no revelan salida cruda ni datos internos del proceso.

## Fuentes y pendientes

- **Decisiones aplicables:** [DEC-011 — alcance del MVP](../../fundacional/decision-log.md#dec-011--alcance-del-mvp), [DEC-012 — contrato común de errores HTTP](../../fundacional/decision-log.md#dec-012--contrato-com%C3%BAn-de-errores-http) como referencia transversal pendiente de formalización específica para Módulo 2, y [documentos de Ping](../ping/).
- **Fuentes técnicas:** [Microsoft Learn — `tracert`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tracert), para los flags `/h`, `/w`, `/d`, la salida `*`, IPv4/IPv6 y el formato general de salida.
- **Pendiente de aprobación o investigación:** comportamiento y respuesta cuando se alcanza el límite de stdout; formalización transversal del contrato de errores para Módulo 2; política de frecuencia; selección de familia para dominios; política IDN/FQDN heredada aún pendiente en Ping.
