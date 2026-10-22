# Requisitos — Información de interfaces de red

## Estado

Especificación objetivo de la herramienta 11 del Módulo 3. El catálogo la marca como pendiente de desarrollo e integración. La aprobación de `psutil` no significa que la dependencia se haya declarado o instalado ni que la herramienta esté implementada.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 3, herramienta 11.
- **Propósito:** mostrar el estado y la configuración de las interfaces de red locales del servidor NetOps Desk.
- **Incluye:** consulta sin parámetros y listado de interfaces con nombre, MAC, IPv4, máscara, gateway, servidores DNS, estado up/down y velocidad en Mbps.
- **No incluye:** cambiar propiedades de interfaces, activar/desactivar adaptadores, consultar equipos remotos o analizar rutas.
- **Familias/protocolos admitidos:** la respuesta expone IPv4 y su máscara; se reporta la dirección MAC asociada a la interfaz. No se especifican campos IPv6 en este contrato v1.

El resultado describe el equipo donde se ejecuta el servidor, no necesariamente el dispositivo que abre la interfaz web.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| IFACE-F-001 | Consultar interfaces sin parámetros | GET sin query ni body | Se lee el estado local de interfaces | Aprobado por la instrucción del usuario |
| IFACE-F-002 | Enumerar propiedades de interfaces | Datos de `psutil.net_if_addrs()` y `psutil.net_if_stats()` | Incluye nombre, MAC, IPv4, máscara, estado y velocidad | Aprobado por la instrucción del usuario |
| IFACE-F-003 | Obtener gateway y DNS por interfaz | Salida de `ipconfig /all` asociada a cada adaptador | `gateway` y `dns_servers` se incorporan a cada interfaz | Aprobado por la instrucción del usuario |
| IFACE-F-004 | Presentar estado y velocidad | Estadísticas de interfaz | `is_up` booleano; velocidad en Mbps y `0` si el sistema no informa valor | Aprobado por la instrucción del usuario |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| IFACE-NF-001 | Rendimiento | Usar psutil para datos de interfaz y evitar subprocess para esos campos | El runner obtiene IP, máscara, MAC, estado y velocidad con psutil | Aprobado por instrucción del usuario |
| IFACE-NF-002 | Ejecución segura | Usar `ipconfig /all` solo para gateway/DNS, con argumentos fijos y `shell=False` | Ningún dato del cliente se incorpora al comando; solo se parsean los campos requeridos | Aprobado por instrucción del usuario |
| IFACE-NF-003 | Concurrencia | Semáforo global `asyncio.Semaphore(5)` | Máximo cinco operaciones concurrentes con un worker de Uvicorn | Aprobado por instrucción del usuario |
| IFACE-NF-004 | Privacidad | La respuesta revela nombres, MAC, IP, gateway y DNS locales | No persistir resultados ni incluir datos innecesarios en logs; revisar exposición antes de habilitar acceso remoto | Requiere revisión de despliegue |

## Criterios de aceptación

- La consulta es GET y no requiere parámetros ni body.
- IP, máscara, MAC, estado y velocidad provienen de `psutil.net_if_addrs()`/`psutil.net_if_stats()`; gateway y DNS se obtienen de `ipconfig /all`.
- Cada interfaz expone `name`, `mac_address`, `ipv4`, `netmask`, `gateway`, `dns_servers`, `is_up` y `speed_mbps` con los tipos del contrato.
- `mac_address`, `ipv4`, `netmask` y `gateway` admiten `null`; `dns_servers` es un array, posiblemente vacío; `speed_mbps` es `0` si el sistema no informa la velocidad.
- `is_up` corresponde al dato de estado de la interfaz y `speed_mbps` está expresado en Mbps.
- La operación usa el semáforo de cinco permisos especificado.

## Fuentes y pendientes

- **Decisiones aplicables:** DEC-011; DEC-017, registrada en [decision-log.md](decision-log.md).
- **Fuente de inventario:** [Catálogo fundacional](../../fundacional/catalogo.md), herramienta 11.
- **Pendientes:** definir selección cuando una interfaz tenga varias IPv4 o gateways, asociación de adaptadores entre psutil e `ipconfig /all`, timeout del comando, política HTTP ante fallos y respuesta al saturar el semáforo.
