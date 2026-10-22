# Arquitectura — Visor de tabla de rutas

> Estado: arquitectura objetivo para la herramienta 14. No hay una implementación específica de Route Table documentada como existente.

## Componentes y responsabilidades

| Capa/componente | Ubicación | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/route_table.py` | Recibir un `RouteTableRunner`, interpretar bytes/resultados y producir rutas IPv4 normalizadas | Biblioteca estándar y protocolo del runner; no importa `subprocess` ni FastAPI |
| Runner/infraestructura | Reutilización o adaptación de `src/netops_desk/api/infrastructure/route_runner.py` | Ejecutar el comando fijo `route print -4`, retornar stdout como bytes y aplicar timeout | `subprocess`, Windows y abstracción del dominio |
| Modelos y API | Modelos/ruta por determinar | Exponer `GET /api/v1/tools/route-table/execute`, coordinar semáforo y serializar respuesta | FastAPI/Pydantic y dominio |
| Interfaz | Integración frontend por determinar | Solicitar y mostrar la tabla de rutas | API y recursos locales |
| Pruebas | Archivos por determinar | Verificar parseo, adaptación del runner, endpoint y presentación | Pytest y fixtures de salida |

## Flujo principal

1. El cliente solicita `GET /api/v1/tools/route-table/execute` sin parámetros ni body.
2. La ruta intenta adquirir uno de los cinco permisos del semáforo global; si no hay permiso disponible, responde HTTP `429` con código `too_many_requests`.
3. El runner ejecuta `route print -4` con argumentos fijos, `shell=False`, captura stdout como bytes y aplica un timeout de 10 segundos.
4. El dominio decodifica la salida con `errors="replace"` y analiza filas por su estructura, no por traducciones de encabezados.
5. El parser acepta únicamente filas con cuatro direcciones IPv4 válidas en orden (destino, máscara, gateway, interfaz) y una métrica entera final. Ignora las filas `On-link`.
6. El dominio devuelve la lista estructurada; si no se aceptó ninguna ruta, devuelve una lista vacía. La API responde con `routes` y libera el permiso en todos los caminos.

## Reutilización del Route Analyzer

La herramienta 10 ya ejecuta `route print -4` mediante `SubprocessRouteRunner` y contiene `_parse_route_table` en `src/netops_desk/route_analyzer.py`. El patrón actual reconoce cuatro tokens con forma IPv4 y un entero final; aunque un comentario lo describe como “3 IPs”, el regex efectivo tiene cuatro grupos de dirección, correspondientes a destino, máscara, gateway e interfaz. El regex limita cada octeto a uno a tres dígitos, pero el nuevo dominio debe validar además que cada valor sea una dirección IPv4 válida.

La nueva herramienta debe reutilizar el adaptador existente o su patrón de parsing para no duplicar una interpretación incompatible del formato. No debe importar el dominio de Route Analyzer desde `route_table.py`. Si se comparte implementación, la integración debe mantener una frontera común de infraestructura o de parser y evitar ejecutar `ipconfig` innecesariamente, ya que Route Table solo necesita `route print -4`.

El parser existente no admite `On-link` como gateway IPv4; esta especificación elige omitir esas filas en v1. La decisión evita inventar una IP y mantiene `gateway` como string IPv4 en el contrato.

## Límites y errores

- **Validación en interfaz:** no hay entradas de usuario; solo presentación de la respuesta.
- **Validación API/dominio:** la solicitud no aporta argumentos. El parser valida las direcciones IPv4 y la métrica antes de producir una fila.
- **Errores y advertencias:** el timeout o fallo del comando produce `DomainError(code="execution_failed")`, que el handler global traduce a HTTP `422`. La saturación del semáforo devuelve HTTP `429` con `too_many_requests`. La salida no parseable requiere una política propia; una tabla sin filas aceptadas es un resultado correcto con `routes: []`.
- **Recursos y seguridad:** ejecutar únicamente `route print -4` sin shell ni datos del request. El comando debe limitarse a 10 segundos. El máximo de bytes leídos de stdout no está definido.

## Concurrencia y evolución

La ruta usará `asyncio.Semaphore(5)` y rechazará inmediatamente la solicitud que no consiga permiso con HTTP `429` y código `too_many_requests`. Un semáforo asyncio es local al proceso; para que el límite sea global entre solicitudes, el despliegue debe usar un único worker Uvicorn.

La separación entre dominio y runner permite probar el parser con fixtures y sustituir la integración de plataforma sin acoplar reglas de parsing a FastAPI. No implica soporte para sistemas operativos distintos de Windows.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** consulta GET sin parámetros; `route print -4`; runner inyectado; timeout de 10 segundos; semáforo global de cinco con `429 too_many_requests`; `DomainError(execution_failed)` mapeado a `422` ante fallo/timeout; tabla vacía con `200` y `routes: []`; parser limitado a cuatro IPv4 válidas y métrica entera; ignorar filas `On-link`; reutilizar adaptador o patrón de la herramienta 10.
- **Alternativas descartadas:** aceptar filtros o comandos enviados por el cliente; interpretar `On-link` como una dirección IP.
- **Dependencias de plataforma/conectividad:** tabla de rutas IPv4 del Windows que ejecuta el servidor; no consulta hosts externos.
- **Límites que permiten evolución futura:** mantener el dominio aislado y reutilizar la integración/parsing existente sin dependencia directa entre dominios.
