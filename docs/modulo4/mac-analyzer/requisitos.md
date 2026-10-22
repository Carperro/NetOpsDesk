# Requisitos — Analizador de direcciones MAC

> Estado: requisitos aprobados para la herramienta 18. La herramienta figura pendiente de desarrollo e integración en el catálogo; este documento no afirma que esté implementada.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 4, herramienta 18.
- **Propósito:** validar, normalizar y analizar una dirección MAC, identificando su fabricante cuando exista en la base OUI local.
- **Incluye:** aceptación de formatos comunes con dos puntos o guiones, normalización canónica y consulta offline del fabricante.
- **No incluye:** consultas a servicios de Internet, escaneo de dispositivos ni inferir identidad, ubicación o propiedad del equipo a partir de la MAC.
- **Familia/protocolo admitido:** direcciones MAC de 48 bits (seis octetos hexadecimales).

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| MAC-F-001 | Aceptar una MAC en formato común con seis octetos hexadecimales separados por `:` o `-`, sin distinguir mayúsculas de minúsculas. | Campo `mac` de tipo string. | La dirección válida se procesa; una dirección con estructura distinta se rechaza. | Aprobado |
| MAC-F-002 | Conservar la entrada original y producir una forma canónica. | MAC válida. | `mac_original` conserva el texto recibido y `mac_normalized` usa minúsculas y dos puntos, por ejemplo `00:1a:2b:3c:4d:5e`. | Aprobado |
| MAC-F-003 | Buscar el fabricante en la base OUI local de `mac-vendor-lookup`. | MAC válida normalizada. | `vendor` contiene el fabricante encontrado o `Desconocido` si no hay coincidencia. | Aprobado |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| MAC-NF-001 | Validación | Aceptar exactamente seis octetos hexadecimales en los separadores documentados; rechazar caracteres y longitudes no válidos. | Los casos inválidos no llegan a la consulta OUI y producen un error de validación. | Aprobado |
| MAC-NF-002 | Concurrencia | La capa API usará `asyncio.Semaphore(5)`. | La operación queda limitada a cinco consultas concurrentes dentro del alcance de despliegue que se defina. | Aprobado; alcance entre workers pendiente |
| MAC-NF-003 | Privacidad y conectividad | La consulta OUI usa una copia local y no requiere enviar la MAC a un servicio externo. | El análisis puede realizarse sin conectividad a Internet. | Aprobado |

## Criterios de aceptación

- `00:1A:2B:3C:4D:5E` y `00-1a-2b-3c-4d-5e` producen `00:1a:2b:3c:4d:5e`.
- La respuesta conserva la representación enviada en `mac_original`.
- Una MAC válida sin fabricante en la base local devuelve `vendor: "Desconocido"` sin fallar la operación.
- Una entrada con octetos no hexadecimales, cantidad incorrecta de octetos o separadores no admitidos se rechaza.
- La consulta de fabricante no depende de una conexión de red externa.

## Fuentes y pendientes

- **Decisiones aplicables:** [DEC-019](decision-log.md#dec-019--uso-de-mac-vendor-lookup-para-identificacion-offline-de-fabricantes-oui).
- **Fuente de alcance:** [catálogo fundacional, herramienta 18](../../fundacional/catalogo.md).
- **Pendiente de aprobación o investigación:** política HTTP y código estable para MAC inválida; comportamiento cuando se agotan los cinco permisos; alcance del semáforo en despliegues con varios workers; versión y proceso de actualización de la base OUI.
