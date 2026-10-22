# Arquitectura — Diagnóstico DNS

## Estado

Arquitectura objetivo; no describe componentes implementados. El catálogo mantiene la herramienta 9 pendiente de desarrollo e integración.

## Componentes previstos

- **Dominio:** `src/netops_desk/dns_test.py` recibirá un `DnsRunner` inyectado. Valida reglas de negocio, solicita una consulta y normaliza el resultado sin importar dnspython, FastAPI ni módulos del navegador.
- **Runner e infraestructura:** el adaptador implementa `DnsRunner` usando `dns.resolver.Resolver`. Si se especifica un resolver, configura ese nameserver; si no, utiliza la configuración DNS del sistema. Ejecuta la consulta síncrona y devuelve un resultado estructurado, no una cadena cruda.
- **API:** los modelos limitan `record_type` a los seis valores admitidos, validan `domain` y validan que `resolver` sea una IP. La ruta `POST /api/v1/tools/dns-test/execute` valida la solicitud, aplica el límite de concurrencia y adapta resultados al contrato HTTP.
- **Frontend:** presentará registros y estados como texto, permitirá seleccionar tipo y resolver y mostrará tiempo de respuesta. La estructura de archivos del frontend no se fija en esta documentación inicial.
- **Pruebas:** el dominio se prueba con un `FakeDnsRunner`; las pruebas HTTP sustituyen el runner. Las pruebas del adaptador simulan respuestas y excepciones DNS, sin depender de resolvers públicos.

## Flujo de consulta

1. La ruta valida el cuerpo y las entradas; la aplicación valida el tipo de contenido conforme al contrato común vigente que se aplique al Módulo 2.
2. La capa API adquiere uno de los diez permisos del semáforo global. El despliegue usa un único worker de Uvicorn para que ese límite sea global.
3. El dominio recibe `domain`, `record_type` y resolver opcional, y llama al runner inyectado.
4. El runner construye un `dns.resolver.Resolver`. Con resolver explícito usa el nameserver indicado; en caso contrario conserva la configuración del sistema.
5. El runner realiza la consulta con un límite de ciclo de vida de 5 segundos y devuelve un resultado estructurado que distingue respuestas, NXDOMAIN y errores DNS. Si dnspython lanza `dns.exception.Timeout`, el adaptador lo conserva como un timeout DNS identificable para la capa API.
6. El dominio transforma los registros en cadenas legibles. Para MX conserva prioridad y servidor; para otros tipos usa una representación textual definida por contrato.
7. La API serializa los campos públicos y libera el permiso en todos los caminos.

## Límites, dependencias y ejecución

- `dnspython` se aprueba mediante DEC-016 porque `socket` no proporciona consultas de los tipos DNS requeridos ni selección del nameserver de consulta.
- La dependencia se importa en la implementación del runner, no en el dominio.
- El límite de 5 segundos debe cubrir la consulta completa y sus reintentos; no basta con limitar cada intento por separado.
- La API usa `asyncio.Semaphore(10)` con un solo worker de Uvicorn. Así el límite es global en el despliegue aprobado; no se deben iniciar varios workers, porque cada proceso tendría su propio semáforo.
- Como la llamada de dnspython es síncrona, debe ejecutarse fuera del event loop (por ejemplo, en el thread pool gestionado por la aplicación) o mediante una operación síncrona compatible con el servidor. Debe verificarse que timeout y cancelación no dejen trabajo residual.
- No crear una capa de servicio adicional salvo que aparezca coordinación real con persistencia u otros casos de uso.

## Resultados y errores

- `success` representa una respuesta con uno o más registros.
- `nxdomain` representa la respuesta DNS que indica que el nombre consultado no existe.
- NXDOMAIN es un resultado válido de la consulta: la API responde HTTP `200 OK`, `status: "nxdomain"` y `records: []`.
- `error` agrupa inicialmente condiciones de consulta fallida que deberán conservar un código interno específico para no confundir timeout, SERVFAIL, ausencia de respuesta y error local.
- `dns.exception.Timeout` se traduce en HTTP `504 Gateway Timeout` con el código `dns_timeout`. La infraestructura adapta la excepción de dnspython a una señal tipada; el dominio no importa la biblioteca y la ruta/API realiza la traducción HTTP.
- Otros errores DNS mantienen pendiente su mapeo HTTP y sus códigos públicos.
- Los mensajes públicos estarán en español y no incluirán trazas ni información interna del sistema.

## Referencias

- [Contrato de API](api-contracts.md).
- [Registro de decisiones](decision-log.md), DEC-016.
- [Arquitectura de Ping](../ping/arquitectura.md).
- [Arquitectura de Traceroute](../traceroute/arquitectura.md).
- [Arquitectura de TCP Test](../tcp-test/arquitectura.md).
- [Contrato común de API del Módulo 1](../../modulo1/api-contracts.md); la extensión al Módulo 2 requiere una decisión transversal.
