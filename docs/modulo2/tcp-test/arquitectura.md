# Arquitectura — Prueba de puertos TCP

## Estado

Arquitectura objetivo; no describe componentes implementados. La inspección de esta tarea no encontró implementación TCP en `src/` ni pruebas TCP en `tests/`.

## Componentes previstos

- **Dominio:** `src/netops_desk/tcp_test.py` recibirá un `TcpRunner` como dependencia. Define validación y clasificación del resultado sin importar `socket`, FastAPI ni módulos del navegador.
- **Runner e infraestructura:** un adaptador `TcpRunner` concreto en la capa de infraestructura realizará la operación de red mediante `socket.create_connection((host, port), timeout)`. El dominio depende de la interfaz; la implementación del runner depende de `socket`.
- **API:** los modelos validan la estructura y los límites de la solicitud y la ruta `POST /api/v1/tools/tcp-test/execute` adapta el request al dominio y traduce resultados al contrato HTTP común que se apruebe para el Módulo 2.
- **Frontend:** la interfaz enviará host, puerto y timeout y mostrará el estado y el tiempo como datos. No se prescribe aquí una estructura de archivos frontend porque la tarea solo especificó la creación de documentación.
- **Pruebas:** pruebas de dominio con un `FakeTcpRunner`; pruebas HTTP de contrato con el runner sustituido. Las pruebas de integración de socket no deben depender de destinos públicos.

## Flujo de ejecución

1. La ruta valida el tipo de contenido y el modelo de solicitud.
2. Se valida el host, el puerto y el timeout conforme a los requisitos.
3. La capa API intenta adquirir inmediatamente uno de los 10 permisos de concurrencia; si no hay permiso disponible, rechaza la solicitud con HTTP `429`.
4. El caso de uso invoca el dominio con el runner inyectado.
5. El runner intenta la conexión y entrega un resultado estructurado o un fallo tipado; no entrega texto crudo para que el dominio lo interprete.
6. El dominio traduce conexión aceptada a `open`, rechazo inmediato a `closed` y timeout de conexión a `filtered`.
7. La infraestructura cierra el socket y la ruta libera el permiso de concurrencia en todos los caminos.
8. La API devuelve el resultado según el contrato documentado.

## Frontera de red y clasificación

- `socket.create_connection((host, port), timeout)` es la operación prevista para el runner.
- Una conexión establecida se clasifica como `open`.
- `ConnectionRefusedError` se clasifica como `closed`.
- `TimeoutError` o `socket.timeout` se clasifica como `filtered`, entendido como ausencia de respuesta dentro del límite configurado.
- `socket.gaierror` y otros `OSError` distintos de timeout y rechazo se traducen en `DomainError(code="host_unreachable")`; el handler de dominio los presenta como HTTP `422`.
- `time_ms` mide, con reloj monotónico, el tiempo total de `socket.create_connection`, incluida la resolución DNS y el handshake TCP.

## Concurrencia y límites

La ruta usará `asyncio.Semaphore(10)`. Un semáforo de asyncio no coordina varios procesos workers.

El timeout de conexión por solicitud está limitado a 10 segundos y la operación completa tiene un límite duro de servidor de 15 segundos. Como la resolución DNS y una llamada de socket bloqueante pueden no obedecer la cancelación de una coroutine de la misma manera que una operación asíncrona, la implementación deberá verificar cómo aplicar el límite exterior sin dejar una operación bloqueante activa. No se debe declarar garantizado el límite total hasta cubrir ese caso.

La ruta usa `asyncio.Semaphore(10)` en modo de rechazo inmediato: si los diez permisos están ocupados, responde HTTP `429 Too Many Requests` sin esperar en cola. Para que el límite sea global en el despliegue local, se requiere un solo worker de Uvicorn; varios workers tendrían semáforos independientes.

## Errores y seguridad

- Las entradas inválidas se rechazan antes de abrir un socket.
- El dominio conserva independencia de HTTP y devuelve errores de dominio tipados.
- La capa de infraestructura conserva el detalle técnico necesario para clasificar fallos; las respuestas públicas no deben exponer rutas internas ni trazas.
- La política de status HTTP y el sobre JSON para errores del Módulo 2 deben alinearse con el contrato común cuando se formalice.
- No se usa `subprocess` ni `shell`; no se ejecutan comandos del sistema operativo.

## Referencias

- [Arquitectura de Ping](../ping/arquitectura.md), runner inyectado y despliegue de un worker.
- [Arquitectura de Traceroute](../traceroute/arquitectura.md), límites de concurrencia y separación de infraestructura.
- [Contrato común de API del Módulo 1](../../modulo1/api-contracts.md), referencia de convenciones HTTP existentes; su extensión al Módulo 2 requiere confirmación.
