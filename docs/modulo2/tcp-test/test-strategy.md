# Estrategia de pruebas — Prueba de puertos TCP

## Estado

Plan de pruebas para la futura implementación. En la revisión estática que acompaña esta especificación no se encontraron archivos de implementación TCP ni pruebas TCP. Ninguna de las pruebas descritas aquí se ejecutó.

## Principios

- Mantener las pruebas de dominio deterministas con un `FakeTcpRunner`; no abrir conexiones a destinos públicos desde la suite.
- Probar por separado las reglas del dominio, la adaptación HTTP y el runner de infraestructura.
- Verificar que cada respuesta corresponde a un comportamiento definido y que errores del sistema no se disfrazan como estados de red.
- Usar fixtures/mocks para simular latencia, timeout, rechazo y fallos de ejecución.

## Matriz de pruebas de dominio

| Caso | Preparación | Resultado esperado |
|---|---|---|
| Conexión exitosa | Fake runner devuelve conexión establecida | `status == "open"`; incluye host, puerto y duración no negativa. |
| Rechazo inmediato | Fake runner produce `ConnectionRefusedError` | `status == "closed"`. |
| Timeout de conexión | Fake runner produce `TimeoutError`/`socket.timeout` | `status == "filtered"`; no afirmar que el firewall es la causa. |
| Puerto mínimo y máximo | Probar 1 y 65535 | Aceptados. |
| Puertos fuera de rango | Probar 0 y 65536 | Error de validación antes de invocar el runner. |
| Tipo de puerto inválido | Probar string, float y boolean | Error de validación antes de invocar el runner. |
| Timeout por defecto | Omitir `timeout_ms` | Runner recibe el valor equivalente a 3000 ms. |
| Timeout mínimo | Probar 500 ms | Aceptado y convertido correctamente a segundos para el runner. |
| Timeout máximo | Probar 10000 ms | Aceptado y convertido correctamente a segundos para el runner. |
| Timeout bajo | Probar menos de 500 ms | Error de validación; runner no invocado. |
| Timeout excesivo | Probar más de 10000 ms | Error de validación; runner no invocado. |
| Host inválido/inyección | Control characters, espacios y caracteres de shell, conforme a la política común | Rechazo antes de invocar runner. |
| Error DNS | Fake runner produce `socket.gaierror` | Dominio produce `DomainError(code="host_unreachable")`; API responde HTTP `422`. |
| Red inalcanzable | Fake runner produce `OSError` distinto de rechazo y timeout | Dominio produce `DomainError(code="host_unreachable")`; API responde HTTP `422`. |

## Matriz de pruebas HTTP

- `POST /api/v1/tools/tcp-test/execute` con request válido y runner falso: comprobar el esquema de respuesta.
- Validar `host`, `port` y `timeout_ms` inválidos con HTTP `422` y los códigos documentados.
- Comprobar el content type no admitido según el contrato HTTP común que se apruebe.
- Comprobar el límite exterior de 15 segundos con runner simulado; asegurar que el status/código sigue la decisión contractual.
- Comprobar concurrencia: 10 ejecuciones admitidas simultáneamente; la siguiente se rechaza inmediatamente con HTTP `429` y `too_many_requests`.
- Probar que `open`, `closed` y `filtered` son resultados HTTP `200`.
- Simular `socket.gaierror` y red inalcanzable; validar HTTP `422` y `host_unreachable`.
- Simular que se exceden los 15 segundos de límite exterior; validar HTTP `504` según el contrato.
- Simular fallo inesperado del runner; validar HTTP `500` según el contrato.

## Pruebas del adaptador de infraestructura

- Sustituir o simular `socket.create_connection` para comprobar host, puerto y timeout recibidos sin realizar tráfico real.
- Verificar cierre del socket después de conexión exitosa y manejo de excepción.
- Verificar traducción diferenciada de conexión aceptada, rechazo inmediato y timeout.
- Comprobar la política para errores distintos de rechazo y timeout cuando se apruebe.
- Revisar que la prueba de límite total cubra también resolución del host y que no deje trabajo bloqueante residual.

## Pruebas de recursos y seguridad

- Comprobar que la solicitud no permite puertos fuera de 1–65535 ni listas/rangos de puertos.
- Verificar liberación del semáforo tras éxito, timeout y excepción.
- Comprobar que el límite de 10 y el rechazo inmediato se aplican con la configuración de un solo worker documentada.
- No usar una conexión pública como criterio de aceptación: depende de firewall, DNS y disponibilidad externa.

## Datos esperados

Los resultados de dominio se validarán con valores controlados por `FakeTcpRunner`, no con la disponibilidad accidental de una máquina externa. Las pruebas de direcciones y parsing de host deben basarse en los casos normativos de la política de validación compartida con Ping. Los casos de integración del socket deben aislarse mediante mocks; cualquier prueba de red real requeriría autorización y no es necesaria para la suite por defecto.

## Referencias

- [Requisitos](requisitos.md).
- [Arquitectura](arquitectura.md).
- [Contrato de API](api-contracts.md).
- [Estrategia de pruebas de Ping](../ping/test-strategy.md).
- [Estrategia de pruebas de Traceroute](../traceroute/test-strategy.md).
