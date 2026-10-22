# Requisitos — Analizador de gateway y rutas

## Estado

Especificación objetivo de la herramienta 10 del Módulo 2. El catálogo la marca como pendiente de desarrollo e integración; los componentes descritos no deben interpretarse como implementación existente.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 2, herramienta 10.
- **Propósito:** identificar el gateway IPv4 por defecto y consultar la tabla de rutas IPv4 local del servidor donde se ejecuta NetOps Desk.
- **Incluye:** ejecución de `ipconfig` y `route print -4`, extracción de gateway y rutas, y presentación de destino, máscara, gateway, interfaz y métrica.
- **No incluye:** modificar la configuración de red, añadir o borrar rutas, analizar rutas IPv6, descubrir la tabla de rutas del equipo del navegador o ejecutar comandos proporcionados por el usuario.
- **Familias/protocolos admitidos:** IPv4 para las filas de ruta de `route print -4`. `ipconfig` puede mostrar otras interfaces/familias, pero el contrato de esta herramienta se limita a rutas IPv4.

El resultado describe la configuración local del servidor. Si la aplicación se ejecuta en otra máquina, no representa automáticamente la red del usuario que abrió la interfaz.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| ROUTE-F-001 | Ejecutar el diagnóstico sin parámetros de entrada | `GET /api/v1/tools/route-analyzer/execute`, sin body | Se inspecciona la configuración local del servidor | Aprobado por la instrucción del usuario |
| ROUTE-F-002 | Identificar el gateway IPv4 por defecto | Salida local de `ipconfig` y/o tabla de rutas | Campo `default_gateway` con la dirección encontrada | Aprobado; selección si hay varias rutas por defecto pendiente |
| ROUTE-F-003 | Devolver rutas IPv4 locales | Salida de `route print -4` | Array de filas con `destination`, `netmask`, `gateway`, `interface` y `metric` | Aprobado por la instrucción del usuario |
| ROUTE-F-004 | Interpretar variaciones de idioma de Windows | Salidas estructuralmente equivalentes en español o inglés | Se obtienen los mismos campos sin depender de un único idioma | Aprobado como objetivo; formatos reales requieren fixtures y verificación |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| ROUTE-NF-001 | Ejecución segura | Adaptador permite exclusivamente `ipconfig` y `route print -4`, en argumentos separados y `shell=False`; no incorpora datos del request en comandos | Pruebas del runner verifican argumentos exactos y ausencia de shell | Aprobado por la instrucción del usuario |
| ROUTE-NF-002 | Tiempo | Timeout máximo de 10 segundos para cada comando | Cada proceso termina o se cancela al alcanzar su límite | Aprobado por la instrucción del usuario |
| ROUTE-NF-003 | Concurrencia | `asyncio.Semaphore(5)` global | Máximo cinco diagnósticos simultáneos en la configuración de despliegue definida | Aprobado; un worker es necesario para que el semáforo en memoria sea global |
| ROUTE-NF-004 | Localización | Capturar stdout/stderr como bytes y decodificar con `errors="replace"`; parsear por estructura y valores numéricos, admitiendo etiquetas de gateway en español e inglés | Fixtures de ambos idiomas producen resultados equivalentes | Aprobado como diseño solicitado; cobertura de formatos pendiente |
| ROUTE-NF-005 | Privacidad | La respuesta contiene información de rutas e interfaces del servidor | No registrar el volcado completo en respuestas o logs públicos; revisar exposición antes de habilitar acceso remoto | Necesita decisión de despliegue/seguridad |

## Criterios de aceptación

- La operación acepta una petición GET sin parámetros, sin requerir body.
- El adaptador ejecuta exactamente `ipconfig` y `route print -4`; no usa `shell=True` ni concatena comandos.
- Cada comando cuenta con su propio timeout de 10 segundos.
- Una salida de `ipconfig` en inglés o español permite identificar la línea de gateway predeterminado; las rutas IPv4 se extraen de filas estructuradas de `route print -4`, no de textos de cabecera fijos.
- Cada ruta devuelta contiene destino, máscara, gateway, interfaz y métrica con tipos coherentes.
- La respuesta no atribuye los datos a la máquina cliente; corresponden al host servidor.
- La política ante comando fallido, salida ilegible, ausencia de gateway y múltiples rutas por defecto se fija antes de implementar.

## Fuentes y pendientes

- **Decisiones aplicables:** DEC-011 (MVP); decisiones específicas de esta herramienta en [decision-log.md](decision-log.md).
- **Fuentes del proyecto:** [Catálogo](../../fundacional/catalogo.md), herramienta 10; [Arquitectura de Ping](../ping/arquitectura.md), runner y salida localizada.
- **Pendiente de aprobación o investigación:** desempate entre varias rutas por defecto; comportamiento si no existe gateway; mapeo HTTP de errores; necesidad de `Cache-Control: no-store`; límite total de ambos comandos (el pedido fija 10 segundos por comando); formatos exactos de las tablas en versiones/localizaciones de Windows.
