# Estrategia de pruebas — Traceroute

> Estrategia prevista. No se afirma que existan o se hayan ejecutado pruebas de Traceroute. Los 210+ tests verdes son contexto aportado por el usuario y no fueron ejecutados durante esta tarea.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Dominio/parser | `tests/test_traceroute_domain.py` | Validación, filas numeradas, IPs, RTTs, asteriscos, orden y límites con `FakeTracerouteRunner` | Pendiente de implementación |
| Adaptador de proceso | `tests/test_traceroute_runner.py` o módulo dedicado | Vector de argumentos, `shell=False`, timeout, límite stdout, terminación y limpieza de proceso | Pendiente; ubicación a decidir al implementar |
| API | `tests/test_api_traceroute.py` | Ruta, esquema, status/error, max_hops, media type, método y errores sin invocar `tracert.exe` real | Pendiente de implementación |
| Interfaz/estático | `tests/test_frontend_static.py` | Recursos locales, estados, accesibilidad básica y presentación de host/saltos con APIs DOM seguras | Pendiente de integrar frontend |
| Integración Windows manual | Procedimiento cuando se autorice | Trazas controladas IPv4/IPv6, destino que responde, routers que filtran y timeout global | Pendiente; requiere autorización de ejecución y conectividad |

## Matriz de casos

| Requisito/caso | Entrada/fixture | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Ruta feliz | Salida fixture de varios saltos con IPs y tres RTTs | Saltos ordenados; IP y tiempos normalizados | Dominio con runner falso | Pendiente |
| Default y máximo | Omitir `max_hops`; usar 30 | Default 15 y máximo aceptado 30 | API/modelo y dominio | Pendiente |
| Límite inválido | 0, 31, booleano, float, string | Rechazo antes del runner; rango aceptado 1–30 y default 15 | Dominio/API | Pendiente de implementación |
| Host IPv4/IPv6/dominio | Literales válidos y nombres de host | Aceptar formas permitidas y entregar argumento de host validado | Dominio/API | Pendiente |
| Inyección por argumentos | `host` con `&`, `|`, `;`, redirecciones, backtick, CR/LF, espacios o prefijo de opción | Rechazo; runner falso no invocado | Dominio/API | Pendiente |
| Flags fijos | Entrada host y límite válidos | `tracert /h max_hops /w 1000 /d host`, sin shell y como vector de argumentos | Adaptador aislado/mockeado | Pendiente de implementación |
| Fila numerada | Líneas con número inicial, whitespace variable y hasta tres duraciones | Número de salto y RTTs extraídos sin depender del texto descriptivo | Parser con fixtures | Pendiente |
| Localización | Fixtures Windows en inglés y español con números equivalentes | Mismos saltos, IPs y tiempos; no depender de frases completas localizadas | Parser | Pendiente |
| Timeout por probe | Una línea con `* * *` y sin IP | No omitir el salto; IP null y `times_ms: []` | Parser | Pendiente de implementación |
| Pérdida parcial | Una o dos mediciones numéricas y otros probes `*` | Incluir solo tiempos numéricos recibidos, sin rellenar con `null` | Parser | Pendiente de implementación |
| Canonicalización IP | IP textual válida e inválida en fila | Canonicalizar IPv4/IPv6; no aceptar fragmento malformado como IP | Parser/dominio | Pendiente |
| Resolución del destino | Cabecera fixture con dominio y dirección final | `resolved_ip` contiene la IP final seleccionada; falta fijar fixtures por versión/locale | Parser | Pendiente |
| Timeout total | Fake/adaptador simula más de 30 s | Proceso terminado y HTTP 504 `traceroute_timeout` | Adaptador/API | Pendiente de implementación |
| Fallo del ejecutable | Runner simula binario ausente | HTTP 500 `execution_failed`, detalle seguro | Contrato API | Pendiente de implementación |
| Límite stdout | Salida justo bajo, igual y por encima de 64 KiB | Nunca retener más de 64 KiB; superar el límite termina la ejecución y emite error seguro | Adaptador | Pendiente de definir error/status |
| Salida malformada o vacía | Texto sin cabecera/fila reconocible | Error controlado; no crear saltos ficticios ni reflejar stdout crudo | Parser/API | Pendiente de definir contrato |
| Concurrencia | Tres ejecuciones ocupan el semáforo; llega una cuarta solicitud | Máximo global 3; cuarta recibe HTTP 429 `too_many_requests`; despliegue de un solo worker | Integración API concurrente | Pendiente de implementación |
| Método y Content-Type | Método distinto de POST; tipo MIME no JSON | 405 y status de media type según contrato común Módulo 2 | API | Pendiente de formalización |

Los resultados esperados del parser deben contrastarse con fixtures reales anonimizados de Windows y revisión manual de salto, dirección y probes. Las definiciones de flags y salida general se contrastan con [Microsoft Learn — `tracert`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tracert). No usar Internet como dependencia del test unitario ni ejecutar procesos reales en tests de dominio/API.

## Ejecución y última verificación

- **Comando:** no ejecutado; esta tarea solo solicita crear documentación.
- **Entorno:** contexto indicado por el usuario: Windows, Python 3.12, FastAPI, Pydantic y Pytest.
- **Fecha:** 2026-10-19.
- **Resultado observado:** no se ejecutaron pruebas; la cifra 210+ proviene del contexto del usuario.
- **Pendientes:** implementar dominio, runner, API, frontend y pruebas; resolver el status/código por exceso de stdout, formalizar el sobre común de errores para Módulo 2 y definir política de familia/DNS; validar fixtures contra versiones/idiomas de Windows y verificar el timeout/cap de salida en una prueba autorizada.
