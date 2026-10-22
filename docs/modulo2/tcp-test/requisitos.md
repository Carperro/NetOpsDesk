# Requisitos — Prueba de puertos TCP

## Estado

Documento de requisitos para la herramienta 8 del MVP. La existencia de esta especificación no implica que la herramienta esté implementada. La documentación se preparó el 2026-10-20 a partir de las decisiones expresas del usuario y de las fuentes vigentes del proyecto.

## Propósito y alcance

Comprobar la conectividad TCP desde el servidor de NetOps Desk hacia un host y puerto indicados. La herramienta devuelve una observación del intento de conexión: `open`, `closed` o `filtered`, junto con el tiempo empleado en determinar el resultado.

La clasificación `filtered` significa que no se recibió una respuesta antes del timeout configurado. No demuestra por sí sola que un firewall haya filtrado el tráfico: también pueden causar el timeout una ruta caída, pérdida de paquetes u otras condiciones de red.

## Requisitos funcionales

| ID | Requisito |
|---|---|
| TCP-F-001 | Aceptar un `host` IPv4, IPv6 o nombre de dominio válido conforme a la política de validación de host acordada para Ping. |
| TCP-F-002 | Aceptar un `port` entero entre 1 y 65535, inclusive. |
| TCP-F-003 | Aceptar `timeout_ms` opcional entre 500 y 10000 ms, inclusive. Si se omite, usar 3000 ms. |
| TCP-F-004 | Intentar una conexión TCP al host y puerto solicitados y devolver `open` si se establece, `closed` si el destino rechaza inmediatamente la conexión y `filtered` si vence el timeout de conexión sin respuesta. |
| TCP-F-005 | Devolver el host solicitado, el puerto, el estado observado y `time_ms`, el tiempo transcurrido para determinar el resultado. |

## Requisitos no funcionales

- **Validación:** validar el host antes de iniciar la conexión, usando la política común de Ping. Rechazar entradas con caracteres de control o contenido que no cumpla esa política. Los detalles de IDN y nombres internacionales siguen sujetos a la definición común de validación.
- **Límite de concurrencia:** la capa API limitará a 10 las operaciones TCP concurrentes mediante `asyncio.Semaphore(10)`. La solicitud que encuentre el límite ocupado se rechaza inmediatamente con HTTP `429`. El límite es global para el despliegue de un solo worker; varios workers multiplicarían la capacidad.
- **Límite de ejecución:** una ejecución no debe ocupar recursos del servidor por más de 15 segundos. El mecanismo para aplicar el límite exterior y su interacción con resolución DNS se debe verificar al implementar.
- **Recursos:** cerrar siempre el socket y liberar el permiso de concurrencia, tanto en resultados normales como ante errores.
- **Separación:** el dominio no depende de `socket`, FastAPI ni del navegador. La operación de red corresponde a un runner inyectado.
- **Seguridad:** la herramienta solo intenta una conexión TCP al host y puerto suministrados. No admite rangos de puertos, barrido de puertos ni ejecución de comandos del sistema operativo.

## Criterios de aceptación

- Un puerto que acepta la conexión produce el estado `open`.
- Un rechazo inmediato (`ConnectionRefusedError`) produce `closed`.
- Un timeout de conexión produce `filtered`, sin presentarlo como prueba concluyente de filtrado por firewall.
- Los puertos 0 y 65536, los valores no enteros y los hosts inválidos se rechazan antes de llamar al runner.
- Si se omite `timeout_ms`, se aplica 3000 ms; se aceptan valores de 500 a 10000 ms y se rechazan los que queden fuera del intervalo.
- La aplicación limita las ejecuciones concurrentes a 10 y aplica un máximo de 15 segundos a la operación completa, sujeto a una implementación que también gestione la resolución del host.
- `open`, `closed` y `filtered` se devuelven como resultados de diagnóstico con HTTP `200 OK`.
- Un error DNS (`socket.gaierror`) o de red inalcanzable (`OSError` distinto de rechazo y timeout) se traduce en `DomainError` con código `host_unreachable` y HTTP `422`.
- `time_ms` incluye la resolución DNS y el handshake TCP medidos durante la llamada completa a `socket.create_connection`.

## Fuera de alcance

- Escaneo de múltiples puertos o destinos.
- Identificación del servicio o versión que escucha en el puerto.
- Garantizar que `filtered` identifica una regla de firewall concreta.
- Diagnóstico de disponibilidad general del host a partir de un único intento TCP.

## Referencias

- [Catálogo de herramientas](../../fundacional/catalogo.md), herramienta 8.
- [Decisiones fundacionales](../../fundacional/decision-log.md), DEC-011 y DEC-012.
- [Requisitos de Ping](../ping/requisitos.md), para la política compartida de host.
- [Requisitos de Traceroute](../traceroute/requisitos.md), para convenciones de herramientas de red del Módulo 2.
- [Plantilla de herramienta](../../plantilla-herramienta/).
