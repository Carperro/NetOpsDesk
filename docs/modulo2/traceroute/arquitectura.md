# Arquitectura — Traceroute

> Arquitectura objetivo para la herramienta 7. No hay implementación de Traceroute ni pruebas específicas creadas en esta tarea; todas las ubicaciones indicadas son destino propuesto.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/traceroute.py` | Validar invariantes, recibir un `TracerouteRunner`, interpretar su resultado estructurado y formar los saltos normalizados. No importa `subprocess` ni FastAPI. | Biblioteca estándar, `ipaddress` y protocolo/interfaz del runner |
| Interfaz del runner | `TracerouteRunner` en el dominio | Abstraer la ejecución y devolver estado, salida acotada y metadatos del proceso; no exponer strings de comando. | Tipos del dominio |
| Adaptador Windows | Capa de infraestructura/API, ubicación por decidir al implementar | Ejecutar `tracert.exe` con argumentos fijos, `shell=False`, deadline de 30 s y límite efectivo de stdout de 64 KiB. Terminar el proceso si vence el timeout o se supera el máximo de salida. | `subprocess`, sistema operativo y contrato del runner |
| Modelos API | `src/netops_desk/api/models/traceroute.py` | Validar JSON, `host` y `max_hops` (opcional, entero estricto entre 1 y 30, default 15). | Pydantic |
| Ruta API | `src/netops_desk/api/routes/traceroute.py` | Validar Content-Type, adaptar solicitud al dominio, inyectar runner y traducir errores al contrato HTTP aprobado. No parsea directamente texto del sistema operativo. | FastAPI, modelos, dominio y adaptador |
| Integración de aplicación | `src/netops_desk/api/main.py` | Registrar router y página cuando se autorice implementar e integrar frontend. | FastAPI |
| Frontend | `src/netops_desk/static/tools/traceroute.html`, `src/netops_desk/static/js/traceroute.js` | Enviar entrada, mostrar progreso/resultado/error, presentar saltos dinámicos como texto seguro. | API y recursos locales |
| Pruebas | `tests/test_traceroute_domain.py`, `tests/test_traceroute_runner.py` (si se separa), `tests/test_api_traceroute.py`; guardas en `tests/test_frontend_static.py` | Probar parser con fixtures y dominio con `FakeTracerouteRunner`; comprobar límites y contratos sin ejecutar trazas reales en unit tests. | Pytest |

La separación sigue el patrón de [arquitectura de Ping](../ping/arquitectura.md). La ubicación exacta del adaptador y el esquema del resultado estructurado se decidirán al implementar, sin añadir capas por anticipado.

## Flujo principal

1. API valida el JSON, el tipo de contenido y los límites de `host` y `max_hops`.
2. Dominio revalida sus invariantes y llama al `TracerouteRunner` inyectado.
3. Adaptador ejecuta `tracert.exe` con `/h <max_hops> /w 1000 /d <host>`, usando un vector de argumentos sin shell.
4. Adaptador aplica timeout total de 30 s y captura stdout de forma acotada a 64 KiB; no debe acumular una salida ilimitada para comprobar el límite después.
5. Dominio procesa solo filas de salto. Identifica el número de salto al inicio, extrae los tiempos numéricos disponibles y valida/canonicaliza la dirección IP cuando aparece.
6. La ruta arma la respuesta JSON y la interfaz muestra las direcciones, tiempos y saltos sin respuesta como texto.

La ruta API aplicará `asyncio.Semaphore(3)` como límite global de tres ejecuciones simultáneas; si no hay un permiso disponible, responde HTTP 429 en vez de dejar una cola sin límite. La aplicación debe desplegarse con un único worker Uvicorn; varios workers tendrían semáforos independientes y romperían la garantía global. La ejecución bloqueante de `tracert.exe` no debe ocupar el event loop de una ruta `async`: usar una ruta síncrona que FastAPI ejecute en su thread pool o delegar explícitamente el trabajo bloqueante a un thread pool.

El deadline global es necesario porque `max_hops` y el timeout por respuesta no garantizan por sí solos un tiempo total breve. A modo de cota conservadora, 30 saltos con tres respuestas que esperen hasta 1 s pueden superar 30 s; el timeout total prevalece y puede terminar la traza antes de completar todos los saltos.

## Ejecución segura en Windows

Vector aprobado para `tracert.exe` en Windows:

```python
["tracert", "/h", str(max_hops), "/w", "1000", "/d", host]
```

- No aceptar flags, ejecutables ni argumentos adicionales enviados por el cliente.
- Usar `shell=False`; nunca concatenar la entrada en una orden de shell.
- Validar host como IPv4, IPv6 o dominio con las mismas reglas de validación de host definidas para Ping. La política exacta de IDN y FQDN sigue pendiente en Ping.
- Microsoft documenta `/d` para evitar resolver a nombres los routers intermedios; el destino puede seguir requiriendo resolución si se recibe como dominio.
- La documentación de Microsoft define `/h` como máximo de saltos, `/w` como espera por respuesta y `/4`/`/6` como selectores de familia. El vector aprobado por el usuario no fuerza `/4` ni `/6`; no se añadirá uno sin decisión sobre selección de familia.
- Para aplicar el límite de stdout durante la ejecución, leer en bloques con una estrategia que corte al superar 64 KiB y termine el hijo. `subprocess.run(capture_output=True)` por sí solo materializa la salida antes de permitir esa comprobación; no satisface estrictamente el límite de memoria.
- La forma de cancelar/terminar el proceso, limpiar recursos y clasificar salida excesiva debe formar parte del resultado estructurado del adaptador. No publicar salida cruda.

## Parseo, localización y datos

- El parser identifica una fila por el número de salto al inicio, no por coincidencia de una frase completa localizada.
- Una fila puede contener hasta tres mediciones de respuesta. Extraer solo los tiempos numéricos asociados a `ms`; `*` significa que una sonda no recibió respuesta dentro de `-w`.
- Si una fila no contiene dirección IP y sus sondas expiraron, normalizarla como `ip: null` y `times_ms: []`, según el ejemplo contractual.
- Las direcciones detectadas se validan con `ipaddress` y se canonicalizan. No asumir que un salto ausente significa que la ruta terminó: routers intermedios pueden no responder.
- Una fila con todas las sondas perdidas se conserva con `ip: null` y `times_ms: []`. En una fila parcial, `times_ms` contiene solo los RTT numéricos recibidos, en orden, sin insertar `null` por cada `*`.
- El destino se considera identificado por `resolved_ip`; no agregar campos a la respuesta sin decisión contractual.

## Límites y errores

- **Validación de interfaz:** facilita la entrada; no es control de seguridad.
- **Validación API/dominio:** aplicar reglas estrictas de host de Ping y validar `max_hops` como entero estricto entre 1 y 30; no permitir booleanos ni coerciones implícitas.
- **Errores y advertencias:** detalles en español y sin trazas, salida cruda ni rutas locales. Los códigos/estados específicos siguen pendientes de formalización para Módulo 2.
- **Recursos y seguridad:** máximo 30 saltos, 1000 ms por respuesta, deadline de 30 s, máximo 64 KiB de stdout retenido por ejecución y tres procesos concurrentes globales mediante `asyncio.Semaphore(3)` con un worker Uvicorn.
- **Conectividad:** DNS y red son dependencias de ejecución. Los routers pueden filtrar ICMP/ICMPv6 o no emitir respuestas TTL-expired; los `*` son resultado válido y no prueban indisponibilidad total del destino.
- **Plataforma:** primera implementación documentada para Windows y `tracert.exe`; no implica soporte aprobado para Linux/macOS.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** dominio separado del proceso mediante runner inyectado; comando fijo sin shell con flags `/h`, `/w` y `/d`; límite de 1–30 saltos con default 15; espera por respuesta de 1000 ms; deadline de 30 s; stdout limitado a 64 KiB; parseo de saltos y `*`; y semáforo global de 3 con un solo worker. Ver [decision-log.md](decision-log.md).
- **Propuestas:** streaming/cancelación para garantizar el tope de salida y códigos de error específicos para stdout excesivo.
- **Alternativas descartadas:** ninguna registrada.
- **Dependencias de plataforma/conectividad:** Windows `tracert.exe`, DNS al usar dominios y red ICMP/ICMPv6.
- **Límites de evolución:** `TracerouteRunner` permite sustituir la integración de plataforma sin introducir `subprocess` en el dominio; no aprueba otro sistema operativo ni otra tecnología de traceroute.

## Referencias

- [Microsoft Learn — `tracert`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tracert)
- [Arquitectura de Ping](../ping/arquitectura.md)
- [Contrato común del Módulo 1](../../modulo1/api-contracts.md)
