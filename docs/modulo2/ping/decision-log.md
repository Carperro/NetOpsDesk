# Registro de decisiones — Ping

Este registro contiene decisiones específicas de Ping. Las decisiones globales se consultan en [`docs/fundacional/decision-log.md`](../../fundacional/decision-log.md). DEC-011 incluye la herramienta 6 en el MVP y sustituye exclusiones históricas incompatibles de DEC-003; no autoriza por sí misma exposición por LAN.

## Decisiones

### PING-DEC-001 — Alcance de entrada y cantidad de paquetes

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** Ping es una herramienta de diagnóstico del Módulo 2 que debe admitir destinos de las dos familias IP y nombres de host.
- **Decisión:** aceptar un `host` IPv4, IPv6 o nombre RFC 1123 y un `count` con default 4, mínimo 1 y máximo 10.
- **Motivo:** instrucción explícita del usuario para el diseño de Ping.
- **Alternativas:** no registradas.
- **Consecuencias:** no se admiten lotes de host ni cantidades ilimitadas; host y count se validan en API y dominio.
- **Aprobación:** instrucción del usuario de documentar la Herramienta 6, 2026-10-19.

### PING-DEC-002 — Separación del dominio y runner inyectable

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** el dominio no debe depender del sistema operativo para poder probarse y evolucionar.
- **Decisión:** `src/netops_desk/ping.py` define interfaz/clase abstracta `PingRunner`; el dominio recibe un runner por parámetro. El adaptador real `SubprocessPingRunner` reside fuera del dominio, en infraestructura/API. Las pruebas usan un `FakePingRunner`.
- **Motivo:** orden explícita de preservar el dominio puro y aislar la integración de sistema operativo.
- **Alternativas:** no registradas.
- **Consecuencias:** `subprocess` no se importa en el módulo de dominio; las rutas/API construyen o inyectan el adaptador.
- **Aprobación:** instrucción del usuario de documentar la Herramienta 6, 2026-10-19.

### PING-DEC-003 — Invocación segura de `ping.exe` en Windows

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** ejecutar un comando con datos del usuario crea riesgo de Command Injection y bloqueo de recursos.
- **Decisión:** llamar `subprocess.run()` con argumentos separados equivalentes a `["ping", "-n", str(count), "-w", "2000", host]`, nunca con `shell=True`; capturar stdout/stderr como bytes y decodificar con `errors="replace"`; aplicar timeout total de 15 segundos.
- **Motivo:** instrucción explícita del usuario y límites defensivos independientes: validación de host, vector de argumentos y timeout de proceso.
- **Alternativas:** no registradas; no se afirma que otras librerías hayan sido evaluadas.
- **Consecuencias:** el timeout `-w` por respuesta no sustituye el timeout total. No se elevan privilegios; la política del firewall todavía puede bloquear ICMP.
- **Aprobación:** instrucción del usuario de documentar la Herramienta 6, 2026-10-19.

### PING-DEC-004 — Parseo resistente a localización

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** las frases de `ping.exe` varían por idioma y versión de Windows.
- **Decisión:** extraer tiempos mediante patrones numéricos asociados a `ms`; no depender de coincidencia exacta con mensajes localizados. El runner entrega un resultado estructurado, no una cadena cruda como resultado de dominio.
- **Motivo:** instrucción explícita del usuario.
- **Alternativas:** no registradas.
- **Consecuencias:** implementar fixtures de salida por idioma/versión y rechazar o representar de forma segura formatos no reconocidos. La representación de `<1ms` y la semántica de `seq` quedan concretadas por DEC-PING-05.
- **Aprobación:** instrucción del usuario de documentar la Herramienta 6, 2026-10-19.

### PING-DEC-005 — Sin elevación de privilegios

- **Estado:** APROBADA como requisito de diseño; verificación por entorno pendiente
- **Fecha:** 2026-10-19
- **Contexto:** la prueba ICMP normal no debe requerir ejecutar el servicio como administrador.
- **Decisión:** no solicitar ni incorporar elevación; ejecutar con los privilegios de la cuenta normal del servicio en Windows.
- **Motivo:** instrucción explícita del usuario.
- **Alternativas:** no registradas.
- **Consecuencias:** firewall local, reglas de red o destino pueden impedir respuestas; la ausencia de respuesta se representa como diagnóstico y no como prueba concluyente de desconexión.
- **Aprobación:** instrucción del usuario; compatibilidad debe verificarse en cada entorno objetivo.

### DEC-PING-05 — Secuencia de respuestas y RTT inferior a 1 ms

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** `ping.exe` no expone de forma fiable el índice de cada intento ICMP, y el formato `<1ms` no contiene un valor decimal exacto.
- **Decisión:** `seq` será un ordinal consecutivo asignado por el parser a cada respuesta exitosa (1..N), sin huecos ni inferencia del intento perdido. El valor `<1ms` se convierte a `0.0` numérico.
- **Motivo:** no inferir pérdidas individuales a partir del orden de respuestas; mantener campos de tiempo numéricos y compatibles con el contrato.
- **Consecuencias:** con cuatro envíos y tres respuestas, `seq` será 1, 2 y 3. Estadísticas y pruebas usarán `0.0` para RTT inferior a 1 ms.
- **Aprobación:** instrucción explícita del usuario, 2026-10-19.

### DEC-PING-06 — Semántica HTTP de timeout y fallo de ejecución

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** pérdida de respuesta ICMP, timeout del proceso y fallo local al ejecutar el binario son resultados de distinta naturaleza.
- **Decisión:** operación completada con 100% de pérdida devuelve HTTP 200; timeout total del subprocess (>15 s) devuelve HTTP 504 `ping_timeout`; fallo al ejecutar el binario devuelve HTTP 500 `execution_failed`; errores de host/count devuelven HTTP 422 (`invalid_host`/`invalid_count`).
- **Motivo:** separar el resultado de diagnóstico de red de fallos de gateway, ejecución y validación.
- **Consecuencias:** la API traduce fallos de infraestructura sin convertirlos en errores de dominio; no expone stdout/stderr ni detalles internos.
- **Aprobación:** instrucción explícita del usuario, 2026-10-19.

### DEC-PING-07 — Límite global de concurrencia

- **Estado:** APROBADA
- **Fecha:** 2026-10-19
- **Contexto:** limitar la cantidad de procesos Ping simultáneos para acotar consumo de recursos.
- **Decisión:** usar `asyncio.Semaphore(5)` en la API; cuando los cinco permisos estén ocupados, rechazar la solicitud sin espera ilimitada y responder HTTP 429 `too_many_requests`. Desplegar Uvicorn con un único worker para que el semáforo sea global.
- **Motivo:** mantener un máximo global de cinco ejecuciones en el despliegue local aprobado.
- **Consecuencias:** no escalar a múltiples workers en esta versión, porque cada proceso tendría un semáforo separado y excedería el límite global.
- **Aprobación:** instrucción explícita del usuario, 2026-10-19.

## Propuestas y decisiones pendientes

### PING-PROP-003 — Frecuencia y exposición

- **Estado:** PROPUESTA; aprobación pendiente antes de exponer la herramienta fuera de un entorno local controlado
- **Fecha:** 2026-10-19
- **Contexto:** `count <= 10` y timeout de 15 s acotan cada proceso, pero no la cantidad de solicitudes simultáneas o repetidas.
- **Decisión propuesta:** definir límites de frecuencia y política de destinos antes de habilitar acceso LAN o multiusuario. El límite de concurrencia quedó aprobado en DEC-PING-07.
- **Motivo:** reducir abuso de red y agotamiento del thread pool/procesos.
- **Alternativas:** autenticación, rate limiting, destinos permitidos o mantener acceso solo local; no resueltas.
- **Consecuencias:** DEC-011 incluye la herramienta en el MVP, pero no autoriza por sí mismo exposición LAN ni autenticación.
- **Aprobación:** pendiente del usuario.

### PING-PROP-005 — Política de nombres DNS

- **Estado:** PROPUESTA; aprobación pendiente
- **Fecha:** 2026-10-19
- **Contexto:** “dominio RFC 1123” no determina por sí solo la política de IDN y punto final absoluto visible en el formulario.
- **Decisión propuesta:** especificar si se admiten nombres ASCII solamente o IDN convertidos a A-label y si se acepta punto final en un FQDN.
- **Motivo:** evitar validadores divergentes entre interfaz, API y dominio.
- **Alternativas:** solo hostname ASCII sin punto final; hostname internacionalizado con IDNA; no se elige todavía.
- **Consecuencias:** afecta regex, normalización, ejemplos y pruebas.
- **Aprobación:** pendiente del usuario.
