# Requisitos — Estado de adaptadores

> Especificación documental para la herramienta 15 del Módulo 3. No describe implementación existente; el catálogo la marca como pendiente de desarrollo e integración.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 3, herramienta 15.
- **Propósito:** mostrar el estado operativo y la velocidad de los adaptadores de red del servidor NetOps Desk.
- **Incluye:** consulta GET sin parámetros que lista los adaptadores con nombre, estado up/down, velocidad en Mbps, MTU y soporte de multicast.
- **No incluye:** cambiar propiedades de adaptadores, activar/desactivar interfaces, consultar equipos remotos, analizar rutas, obtener IPs ni servidores DNS.
- **Familias/protocolos admitidos:** esta herramienta no procesa direcciones IP ni DNS; solo lee el estado físico/lógico del adaptador mediante `psutil.net_if_stats()`. No se especifican campos de dirección en este contrato v1.

El resultado describe el equipo donde se ejecuta el servidor, no el dispositivo que abre la interfaz web.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| ADP-F-001 | Consultar adaptadores sin parámetros | GET sin query ni body | Se lee el estado local de adaptadores | Aprobado por la instrucción del usuario |
| ADP-F-002 | Enumerar propiedades de adaptador | Datos de `psutil.net_if_stats()` | Incluye nombre, estado, velocidad, MTU y multicast | Aprobado por la instrucción del usuario |
| ADP-F-003 | Presentar estado operativo | Estadísticas de interfaz | `is_up` booleano | Aprobado por la instrucción del usuario |
| ADP-F-004 | Presentar velocidad en Mbps | Estadísticas de interfaz | `speed_mbps` entero en Mbps; `0` si el sistema no informa valor | Aprobado por la instrucción del usuario |
| ADP-F-005 | Presentar MTU | Estadísticas de interfaz | `mtu` entero | Aprobado por la instrucción del usuario |
| ADP-F-006 | Presentar soporte de multicast | Estadísticas de interfaz | `is_multicast` booleano | Aprobado por la instrucción del usuario |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| ADP-NF-001 | Rendimiento | Usar `psutil.net_if_stats()` y evitar subprocess para los campos de esta herramienta | El runner obtiene estado, velocidad, MTU y multicast con psutil | Aprobado por instrucción del usuario |
| ADP-NF-002 | Concurrencia | Semáforo global `asyncio.Semaphore(5)` | Máximo cinco operaciones concurrentes con un worker de Uvicorn | Aprobado por instrucción del usuario |
| ADP-NF-003 | Privacidad | La respuesta revela nombres y propiedades físicas de adaptadores del servidor | No persistir resultados ni incluir datos innecesarios en logs; revisar exposición antes de habilitar acceso remoto | Requiere revisión de despliegue |
| ADP-NF-004 | Aislamiento del dominio | El dominio no importa `psutil` ni accede al sistema operativo | El dominio recibe un runner inyectado y solo valida la estructura de los resultados | Aprobado por la instrucción del usuario |

## Criterios de aceptación

- La consulta es GET y no requiere parámetros ni body.
- Estado, velocidad, MTU y multicast provienen de `psutil.net_if_stats()`.
- Cada adaptador expone `name`, `is_up`, `speed_mbps`, `mtu` e `is_multicast` con los tipos del contrato.
- `speed_mbps` es `0` si el sistema no informa la velocidad.
- `is_up` corresponde al dato de estado de la interfaz informado por psutil.
- La operación usa el semáforo de cinco permisos especificado.

## Fuentes y pendientes

- **Decisiones aplicables:** DEC-011; DEC-017, registrada en `decision-log.md`.
- **Fuente de inventario:** [Catálogo fundacional](../../fundacional/catalogo.md), herramienta 15.
- **Pendientes:** política HTTP ante fallos de psutil o respuesta parcial; conducta al saturar el semáforo; definir el tipo entero de `mtu` y `speed_mbps` en el contrato común del Módulo 3; verificar el soporte de multicast en la versión de `psutil` instalada.