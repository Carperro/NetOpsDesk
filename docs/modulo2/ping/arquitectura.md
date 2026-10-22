# Arquitectura — Ping

> Arquitectura objetivo aprobada en sus límites principales. No hay aún componentes Ping en `src` ni pruebas específicas en `tests`.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/ping.py` | Validar invariantes, invocar la abstracción `PingRunner`, interpretar el resultado estructurado y calcular estadísticas. No conoce HTTP ni crea procesos. | Biblioteca estándar y la interfaz abstracta `PingRunner`; nunca `subprocess` |
| Interfaz del runner | `PingRunner` en el dominio | Contrato para ejecutar una prueba y devolver resultado estructurado: código de salida, stdout/stderr como bytes, timeout/estado de ejecución. | Tipos de dominio |
| Adaptador de sistema operativo | `src/netops_desk/api/infrastructure/ping_runner.py` (ubicación objetivo, pendiente de confirmar con la estructura al implementar) | Implementar `SubprocessPingRunner` en Windows, invocar `ping.exe`, capturar bytes y traducir excepciones del proceso a un resultado tipado. | `subprocess`, sistema operativo y dominio |
| Modelo API | `src/netops_desk/api/models/ping.py` | Validar forma JSON, `host` y límites visibles de `count`; default 4, rango 1–10. | Pydantic |
| Ruta API | `src/netops_desk/api/routes/ping.py` | Adaptar HTTP a dominio, inyectar el runner y convertir resultado a respuesta. No parsea salida del sistema operativo. | FastAPI, modelo, dominio y adaptador |
| Integración de aplicación | `src/netops_desk/api/main.py` | Registrar router y, cuando corresponda, página estática. | FastAPI |
| Frontend | `src/netops_desk/static/tools/ping.html`, `src/netops_desk/static/js/ping.js` | Enviar host/count, exponer estados y presentar datos como texto seguro. | API y assets locales |
| Pruebas | `tests/test_ping_domain.py`, `tests/test_ping_runner.py` (si se separa el adaptador), `tests/test_api_ping.py`; guardas frontend en `tests/test_frontend_static.py` | Probar dominio con `FakePingRunner`, adaptador, contrato API y presentación segura. | Pytest; sin ejecutar ping real en tests unitarios |

Las ubicaciones son un diseño de destino, no archivos existentes. El adaptador puede ubicarse en otro módulo de infraestructura si la estructura aprobada al implementar lo justifica; dominio y transporte deben conservar las fronteras descritas.

## Flujo principal

1. La API valida el objeto de entrada y la dependencia común de contenido JSON.
2. El dominio vuelve a validar `host` y `count` como invariantes para clientes distintos de HTTP.
3. La ruta inyecta una instancia de `PingRunner`; las pruebas inyectan un `FakePingRunner` sin invocar el sistema operativo.
4. `SubprocessPingRunner` invoca la herramienta de Windows usando lista de argumentos, `shell=False`, captura binaria y un timeout de proceso de 15 segundos.
5. El runner devuelve un objeto estructurado. Nunca entrega una cadena de comando ni decide la semántica del dominio.
6. El dominio decodifica stdout/stderr con `errors="replace"`, extrae IP y tiempos, valida consistencia y calcula estadísticas. La ruta forma la respuesta JSON.

La ruta API aplicará `asyncio.Semaphore(5)` como límite global de cinco ejecuciones simultáneas y responderá HTTP 429 si no hay un permiso disponible al admitir la solicitud; la adquisición no debe dejar solicitudes excedentes esperando sin límite. La aplicación debe desplegarse con un único worker Uvicorn; varios workers tendrían semáforos independientes y romperían la garantía global. La ejecución bloqueante de `subprocess.run()` no debe ocupar el event loop de una ruta `async`: usar una ruta síncrona que FastAPI ejecute en su thread pool o delegar explícitamente el trabajo bloqueante a un thread pool. El límite de 15 segundos acota cada trabajo.

## Ejecución segura en Windows

La invocación objetivo es equivalente a:

```python
subprocess.run(
    ["ping", "-n", str(count), "-w", "2000", host],
    shell=False,
    capture_output=True,
    timeout=15,
)
```

- `host` es siempre el último argumento y se valida antes de construir la lista. No se acepta ninguna opción del ejecutable desde el cliente.
- No usar `shell=True`, `os.system`, `cmd.exe /c`, concatenación ni interpolación de cadenas de shell.
- `/n` limita la cantidad de solicitudes. `/w 2000` limita la espera por una respuesta individual; `timeout=15` es el límite duro del proceso completo. Con `count=10`, el timeout global puede interrumpir la operación antes de que se consuman diez esperas completas.
- `capture_output=True` mantiene `stdout` y `stderr` como bytes. Decodificar después explícitamente con `decode(..., errors="replace")`; no asumir cp1252, cp850 ni UTF-8.
- La resolución del ejecutable debe apuntar a la utilidad del sistema operativo y no a una ruta controlable por la solicitud. No aceptar ruta del binario desde el cliente.
- Ante timeout, finalizar el proceso y representar el fallo de forma estructurada; no exponer `TimeoutExpired`, salida cruda, ruta local ni detalles internos.

La documentación de Microsoft confirma el propósito de `/n` y que `/w` es una espera por respuesta, no un deadline total. `subprocess.run(timeout=...)` proporciona el límite total independiente.

## Parseo, localización y dominio

- El parseo acepta texto de salida en inglés o español sin depender de frases completas como “Request timed out” o “Tiempo de espera agotado”. La extracción de RTT busca un valor numérico inmediatamente asociado a `ms`; la estructura de respuesta y la IP se validan por separado.
- La IP resuelta debe validarse y canonicalizarse con `ipaddress` antes de incluirse en `resolved_ip`.
- No inferir una respuesta recibida de la línea de resumen de latencia: los patrones deben distinguir respuestas individuales de estadísticas finales. Mantener fixtures reales anonimizados por idioma/versión de Windows.
- La salida `"<1ms"` se convierte a `0.0` (float); los campos de tiempo no contienen strings. Esta es una convención contractual, no una medición decimal exacta.
- `ping.exe` no ofrece necesariamente un número de secuencia ICMP por cada línea de respuesta. El parser asigna a las respuestas exitosas un ordinal consecutivo 1..N; no representa el índice del intento y no adivina huecos para paquetes perdidos.
- La lógica de cálculo de pérdida y estadísticas recibe resultados tipados, por lo que se puede probar sin conectividad ni subprocess.

## Límites y errores

- **Validación de interfaz:** orienta al usuario; no es control de seguridad.
- **Validación API/dominio:** tipo de host, sintaxis IP/dominio, caracteres permitidos y `count` 1–10 se vuelven a validar en el dominio. Rechazar whitespace/control characters y metacaracteres antes del runner.
- **Errores y advertencias:** los errores públicos deben tener códigos estables, mensajes en español y no filtrar stdout/stderr. La salida con 100% de pérdida es un diagnóstico completado, no una excepción interna.
- **Recursos y seguridad:** 10 paquetes máximo, 15 segundos por proceso y cinco ejecuciones simultáneas globales con un solo worker; no aceptar listas de hosts. La política de frecuencia y exposición fuera del equipo sigue pendiente.
- **Acceso a red:** el usuario puede especificar cualquier destino válido; la herramienta no verifica que el objetivo sea seguro, alcanzable o autorizado. La exposición por LAN y los controles de abuso requieren aprobación separada. DEC-011 incluye Ping en el MVP, no aprueba exposición LAN.
- **Privilegios:** no elevar el proceso ni solicitar administrador. El firewall local/de destino puede afectar el resultado.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** separación por `PingRunner`, inyección de dependencia, adaptador basado en `subprocess.run` sin shell, ejecución Windows con `-n`/`-w`, bytes con decodificación tolerante, timeout global de 15 s y parseo no dependiente de frases localizadas; véase [decision-log.md](decision-log.md).
- **Alternativas descartadas:** no registradas; no afirmar que una librería ICMP haya sido evaluada.
- **Dependencias de plataforma/conectividad:** implementación inicial para Windows y `ping.exe`; la prueba requiere conectividad y puede estar afectada por DNS/firewall. La capa de dominio se conserva independiente de esa plataforma.
- **Límites de evolución:** `PingRunner` permite sustituir el adaptador por otro sistema operativo o mecanismo de prueba sin importar `subprocess` en el dominio. No implica aprobación de Linux/macOS.
