# Estrategia de pruebas — Ping

> Estrategia prevista. No hay pruebas de Ping implementadas ni ejecutadas. Las 210 pruebas indicadas en la solicitud son un dato de contexto del usuario y no una verificación realizada durante esta tarea.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_ping_domain.py` | Validación, conteo, parsing localizado, estadísticas, pérdida, resultados parciales/timeout mediante `FakePingRunner` | Pendiente; archivo inexistente |
| Adaptador de proceso | `tests/test_ping_runner.py` o casos dentro de `test_ping_domain.py` | Argumentos separados, `shell=False`, timeout 15 s, salida binaria y conversión de `TimeoutExpired` a resultado estructurado | Pendiente; decidir ubicación al implementar |
| API | `tests/test_api_ping.py` | Ruta, entrada, default, 1/10, errores, media type, método y respuesta sin ejecutar `ping.exe` real | Pendiente; archivo inexistente |
| Interfaz/estático | `tests/test_frontend_static.py` | Carga de recursos locales, datos dinámicos mediante `textContent`, mensajes en español y estados carga/éxito/error | Pendiente; no modificar ni ampliar en esta tarea |
| Integración Windows manual | Procedimiento documentado al integrar | Ping local/controlado, host DNS y destino sin respuesta; revisar timeout, versión/idioma de Windows y firewall | Pendiente; requiere entorno y autorización de ejecución |

## Matriz de casos prevista

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Default | Host válido, sin `count` | 4 solicitudes | `test_api_ping.py` | Pendiente |
| Límites de cantidad | `count` 1 y 10 | Aceptados; lista de argumentos usa el mismo valor | Dominio, adaptador y API | Pendiente |
| Cantidad fuera de límites | `count` 0, 11, float, string, boolean | Rechazo antes del runner | Dominio y API | Pendiente |
| IPv4 e IPv6 | IPs válidas e inválidas | Aceptar literales válidos; normalizar `resolved_ip`; rechazar formatos inválidos y zone IDs | Dominio con runner falso | Pendiente |
| Hostname RFC 1123 | Labels válidas, longitud límite, guion inicial/final, label >63 y total fuera de rango | Solo formas de host permitidas | Dominio/API | Pendiente |
| Inyección por argumento | `host` con `&`, `\|`, `;`, `>`, `<`, backtick, CR/LF, tab, NUL, espacios, URL o prefijo de opción | Rechazo; el runner falso confirma que no fue invocado | Dominio/API | Pendiente |
| Invocación del proceso | Entrada válida | Lista `ping -n count -w 2000 host`, `shell=False`, `capture_output=True`, `timeout=15`; host final | Adaptador aislado/mockeado | Pendiente |
| Decodificación | stdout/stderr en bytes con UTF-8 inválido | Decodifica con reemplazo; no lanza `UnicodeDecodeError` | Adaptador/parser | Pendiente |
| Localización | Fixtures de salida inglesa y española equivalentes | Mismos IPs, RTTs y estadísticas sin depender de frases completas | Dominio/parser | Pendiente |
| Pérdida parcial | 2 respuestas válidas de 4 | recibidos 2; pérdida 50%; min/max/avg exactos | Dominio | Pendiente |
| Sin respuesta | 0 de 4 | Pérdida 100%; respuestas vacías; min/max/avg `null`; resultado de dominio completado | Unitario con `FakePingRunner` sin respuestas; API 200 | Pendiente de implementación |
| RTT menor de 1 ms | Salida `<1ms` | `time_ms` y estadística correspondiente se representan como `0.0` numérico | Unitario con `FakePingRunner` | Pendiente de implementación |
| Secuencia de respuestas | 3 respuestas de 4 envíos | `seq` 1, 2, 3 sin huecos; nunca inferir el intento perdido | Unitario con `FakePingRunner` | Pendiente de implementación |
| IP resuelta | Dominio con nombre que resuelve | Dirección seleccionada se valida y canonicaliza | Fixture/parser e integración controlada | Pendiente |
| Timeout global | Runner excede 15 s | Proceso terminado; HTTP 504 `ping_timeout` | Contrato API con timeout simulado en runner | Pendiente de implementación |
| Fallo del ejecutable | Runner simula binario ausente u otro fallo de inicio | HTTP 500 `execution_failed`, detalle seguro | Contrato API con caída del runner simulada | Pendiente de implementación |
| Salida no reconocida | Texto vacío o formato no soportado | Error tipado; no producir estadísticas ficticias ni exponer texto crudo | Dominio/parser | Pendiente |
| Concurrencia | Seis solicitudes simultáneas con cinco ejecuciones ocupadas | Máximo global de cinco; exceso recibe HTTP 429 `too_many_requests`; un solo worker Uvicorn | Prueba de contrato/integración concurrente | Pendiente de implementación |

Los valores de referencia para pérdida/estadísticas se calculan manualmente a partir de respuestas fixture. Las reglas de hostname se contrastan con RFC 1123, sección 2.1; el comportamiento de flags `/n` y `/w` se contrasta con documentación de Microsoft. Los fixtures de Windows deben capturarse y revisarse por locale/version sin incluir destinos o datos sensibles.

## Ejecución y última verificación

- **Comando:** no ejecutado; la tarea autoriza crear documentación, no requiere correr pruebas.
- **Entorno:** contexto de usuario: Windows, Python 3.12, FastAPI, Pydantic y Pytest.
- **Fecha:** 2026-10-19.
- **Resultado observado:** no se ejecutaron pruebas. La cifra de 210 pruebas verdes proviene del contexto indicado por el usuario y no fue reproducida.
- **Pendientes:** implementar dominio/runner/ruta/interfaz y pruebas; resolver la política DNS IDN/punto final y controles de acceso/frecuencia; verificar salida de `ping.exe` en Windows y al menos dos locales antes de afirmar compatibilidad del parser.
