# Requisitos — Catálogo de puertos y protocolos

> Estado: alcance aprobado para la herramienta 19. El catálogo fundacional la marca pendiente de desarrollo e integración; este documento no afirma que esté implementada.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 4, herramienta 19.
- **Propósito:** consultar información local sobre puertos TCP/UDP conocidos, sus servicios y usos habituales.
- **Incluye:** búsqueda por número de puerto o nombre de servicio; presentación de protocolo y descripción; listado completo cuando no se indica búsqueda.
- **No incluye:** sondeo de puertos, verificación de disponibilidad, consulta de red ni edición del catálogo desde la interfaz.
- **Protocolos admitidos:** TCP y UDP.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| PORT-F-001 | Buscar por número de puerto o nombre de servicio. | Texto de búsqueda opcional. | La respuesta contiene registros coincidentes con el texto. | Aprobado |
| PORT-F-002 | Comparar sin distinguir mayúsculas/minúsculas y permitir coincidencias parciales. | Consulta sobre nombre o servicio, por ejemplo `HTT`. | Se incluyen los registros cuyo campo de búsqueda contiene la consulta sin distinguir el uso de mayúsculas. | Aprobado |
| PORT-F-003 | Devolver el catálogo completo si la búsqueda está vacía. | Consulta omitida o vacía. | Se devuelve la lista completa del dataset local. | Aprobado |
| PORT-F-004 | Informar número, protocolo, servicio y descripción. | Registro del catálogo. | Cada elemento contiene `port`, `protocol`, `service` y `description`. | Aprobado |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| PORT-NF-001 | Datos | El dominio mantiene un dataset local estático con al menos 20 registros de puertos comunes. | La cantidad de registros incluidos es igual o superior a 20. | Aprobado |
| PORT-NF-002 | Concurrencia | La capa API usa `asyncio.Semaphore(5)`. | La búsqueda se ejecuta bajo el semáforo de cinco permisos. | Aprobado; conducta de saturación pendiente |
| PORT-NF-003 | Dependencias y conectividad | La consulta es de lectura local y no requiere base de datos, `subprocess` ni red. | La respuesta se forma a partir del dataset local. | Aprobado |

## Criterios de aceptación

- Una consulta `80` encuentra el registro HTTP correspondiente.
- Una consulta `http` o `HTT` encuentra coincidencias sin distinguir mayúsculas y con coincidencia parcial.
- Una consulta vacía u omitida devuelve el catálogo completo.
- Cada resultado contiene un número de puerto, protocolo TCP o UDP, nombre de servicio y descripción.
- El dataset contiene al menos 20 registros.
- La herramienta no ejecuta sondeos de red ni depende de conectividad externa.

## Fuentes y pendientes

- **Decisiones aplicables:** [PORT-DEC-01 y PORT-DEC-02](decision-log.md).
- **Fuente de alcance:** [catálogo fundacional, herramienta 19](../../fundacional/catalogo.md).
- **Pendiente de aprobación o investigación:** selección y fuentes de los registros iniciales; si la búsqueda parcial numérica aplica como subcadena; orden de resultados y tratamiento de consultas solo con espacios; conducta HTTP cuando el semáforo está agotado.
