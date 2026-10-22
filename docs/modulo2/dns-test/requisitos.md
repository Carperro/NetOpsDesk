# Requisitos — Diagnóstico DNS

## Estado

Documento de diseño para la herramienta 9 del Módulo 2. El catálogo la marca como pendiente de desarrollo e integración. La aprobación de `dnspython` como dependencia se registra en DEC-016 de este conjunto documental; no implica que se haya instalado ni que exista implementación.

## Propósito y alcance

Consultar registros DNS de un dominio y permitir comparar los resultados obtenidos mediante diferentes resolvers. La operación devuelve los registros encontrados, el tiempo de consulta y un estado de diagnóstico.

## Requisitos funcionales

| ID | Requisito |
|---|---|
| DNS-F-001 | Aceptar un `domain` que sea un nombre de dominio, no una URL. |
| DNS-F-002 | Aceptar `record_type` de la lista cerrada `A`, `AAAA`, `MX`, `TXT`, `NS` y `CNAME`. |
| DNS-F-003 | Aceptar `resolver` opcional como dirección IP de un servidor DNS. Si se omite, usar la configuración DNS del sistema. |
| DNS-F-004 | Consultar el tipo solicitado y devolver `domain`, `record_type`, `resolver`, `status`, `time_ms` y `records`. |
| DNS-F-005 | Representar el resultado con estados de diagnóstico `success`, `nxdomain` o `error`. |
| DNS-F-006 | Convertir cada respuesta DNS en una cadena legible. Para MX incluir prioridad y servidor, por ejemplo `10 smtp.google.com`. |

## Requisitos no funcionales

- **Validación de dominio:** rechazar esquemas (`http://`, `https://`), rutas, query strings, fragmentos, credenciales, puertos, espacios y caracteres de control. La política de IDN, punto final absoluto y límites precisos por etiqueta debe quedar definida antes de implementar.
- **Validación del resolver:** si se proporciona, debe ser una dirección IPv4 o IPv6 literal; no resolver el nombre del propio servidor DNS.
- **Timeout:** cada consulta debe finalizar en un máximo de 5 segundos, incluyendo reintentos de la biblioteca. La implementación debe limitar el ciclo completo de consulta, no solamente un intento individual.
- **Concurrencia:** la capa API usará `asyncio.Semaphore(10)`. El alcance del límite (por proceso o global) y la conducta al saturarse deben especificarse al implementar; un semáforo asyncio no coordina varios procesos workers.
- **Rendimiento:** la consulta síncrona de dnspython no debe bloquear el event loop de FastAPI. Debe ejecutarse en un contexto apropiado y comprobar que el límite total de 5 segundos se respeta también allí.
- **Aislamiento:** el dominio recibe un `DnsRunner` inyectado y no importa dnspython ni depende de FastAPI.
- **Privacidad y recursos:** no persistir consultas ni resultados; no exponer detalles internos del resolver. No consultar el DNS desde la suite de pruebas contra servidores públicos.

## Criterios de aceptación

- Se aceptan únicamente los seis tipos de registro especificados.
- Se rechazan entradas que sean URLs o dominios inválidos antes de invocar el runner.
- Cuando `resolver` se omite, el runner usa la configuración DNS del sistema; cuando se indica una IP, la consulta se dirige a ese nameserver.
- A, AAAA, MX, TXT, NS y CNAME producen registros en texto legible, con MX expresado como prioridad y servidor.
- Una respuesta positiva se informa como `success`; NXDOMAIN y otros errores DNS se distinguen mediante estados de diagnóstico, sin confundir NXDOMAIN con un fallo HTTP de validación.
- La consulta se limita a 5 segundos y se verifica que una respuesta lenta no bloquee el event loop.
- La capa API incorpora un semáforo de 10 operaciones concurrentes; el alcance y la conducta ante saturación se resuelven antes de implementar.

## Decisiones pendientes

- Política exacta de dominios IDN, FQDN con punto final y normalización de mayúsculas.
- Valor de respuesta de `resolver` cuando se usa el DNS del sistema (por ejemplo, `null` o el nameserver efectivo).
- Formato textual estable de registros TXT y normalización del punto final en nombres de destino.
- Estados HTTP y códigos de error para NXDOMAIN, timeout DNS, SERVFAIL, ausencia de respuesta y errores locales.
- Semántica de admisión del semáforo y alcance global del límite de concurrencia.

## Fuera de alcance

- Transferencias de zona DNS (`AXFR`/`IXFR`).
- Consultas recursivas arbitrarias, tipos de registro no incluidos en la lista permitida o edición de zonas.
- Modificar la configuración DNS del sistema.
- Afirmar que una respuesta obtenida de un resolver es autoritativa o que todos los resolvers deben coincidir.

## Referencias

- [Catálogo de herramientas](../../fundacional/catalogo.md), herramienta 9.
- [Decisiones fundacionales](../../fundacional/decision-log.md), DEC-011 y DEC-012.
- [Registro de decisiones de DNS](decision-log.md), DEC-016 y decisiones específicas.
- [Requisitos de Ping](../ping/requisitos.md), como referencia para validación de nombres y diagnóstico de red.
- [Requisitos de Traceroute](../traceroute/requisitos.md) y [TCP Test](../tcp-test/requisitos.md), para límites de recursos de herramientas del Módulo 2.
