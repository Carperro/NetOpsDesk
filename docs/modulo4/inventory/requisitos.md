# Requisitos — Inventario de dispositivos

> Estado: requisitos contrastados estáticamente con la implementación disponible. El catálogo fundacional todavía marca la herramienta 16 como pendiente, por lo que su estado de gobernanza debe reconciliarse allí en una tarea autorizada.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 4, herramienta 16.
- **Propósito:** gestionar un inventario básico de dispositivos de red.
- **Incluye:** dar de alta, listar, editar y eliminar dispositivos con nombre, dirección IP, tipo de equipo, ubicación y observaciones; persistencia local mediante SQLite.
- **No incluye:** autenticación, acceso por LAN, detección automática de dispositivos, manejo de sesiones de usuario ni integración con sistemas externos.
- **Familias/protocolos admitidos:** direcciones IPv4 para el campo `ip_address`. No se valida IPv6 en esta herramienta.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| INV-F-001 | Crear un dispositivo | Nombre, IP, tipo, ubicación y observaciones | El dispositivo queda registrado en la base de datos y se asigna un `id` autoincremental | Implementado |
| INV-F-002 | Listar todos los dispositivos | Solicitud sin parámetros | Se devuelven todos los dispositivos registrados, ordenados por `id` descendente | Implementado |
| INV-F-003 | Editar un dispositivo existente | `id`, `name` e `ip_address` requeridos; campos restantes opcionales con default `""` | Se actualiza el dispositivo; los campos opcionales omitidos se guardan como cadena vacía | Implementado |
| INV-F-004 | Eliminar un dispositivo | `id` existente | El dispositivo se elimina de la base de datos | Implementado |
| INV-F-005 | Eliminar un dispositivo inexistente | `id` inexistente | El dominio lanza `DomainError(not_found)` y la API devuelve HTTP 422 | Implementado |
| INV-F-006 | Editar un dispositivo inexistente | `id` inexistente y cuerpo válido | El dominio lanza `DomainError(not_found)` y la API devuelve HTTP 422 | Implementado |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| INV-NF-001 | Validación de dominio | La IP debe ser IPv4 válida | Una IP inválida produce HTTP 422 con código `invalid_ip` | Implementado |
| INV-NF-002 | Validación de dominio | El nombre debe ser una cadena no vacía luego de quitar espacios externos | Nombre vacío/blanco produce HTTP 422 `invalid_name`; campo ausente produce HTTP 422 `missing_field` por validación Pydantic | Implementado |
| INV-NF-003 | Persistencia | La base de datos `netops.db` se crea automáticamente si no existe | Al ejecutar la aplicación por primera vez, el archivo y la tabla `devices` quedan disponibles | Implementado |
| INV-NF-004 | Seguridad y privacidad | La base de datos es local; no se exponen datos a redes externas | El repositorio usa `netops.db` relativo al directorio de trabajo. En el estado auditado el archivo está rastreado por Git y `.gitignore` no contiene una regla para él | Discrepancia observada; remediación fuera de este pase documental |
| INV-NF-005 | Operación | La aplicación funciona en modo local sin dependencias de red | No se requiere conectividad externa para usar el inventario | Aprobado |

## Criterios de aceptación

- Crear un dispositivo con datos válidos devuelve HTTP 201 con el objeto creado, incluyendo su `id`.
- Listar devuelve HTTP 200 con la lista completa de dispositivos.
- Editar un dispositivo existente con `name` e `ip_address` devuelve HTTP 200 con los datos actualizados; los campos opcionales omitidos pasan a `""`.
- Eliminar un dispositivo existente devuelve HTTP 204 sin contenido.
- Una IP inválida (por ejemplo, `999.999.999.999`) devuelve HTTP 422 `invalid_ip`.
- Un nombre vacío o blanco devuelve HTTP 422 `invalid_name`; un campo `name` ausente produce HTTP 422 `missing_field`.
- Un `id` inexistente en PUT o DELETE devuelve HTTP 422 `not_found` a través del handler global de `DomainError`.
- La base `netops.db` se crea respecto del directorio de trabajo; en el estado auditado está rastreada en Git, por lo que no se afirma que esté ignorada.

## Fuentes y pendientes

- **Decisiones aplicables:** DEC-018 (SQLite nativo y patrón Repository).
- **Fuentes técnicas verificadas:** catálogo en `docs/fundacional/catalogo.md` (herramienta 16).
- **Pendiente de aprobación o investigación:** el catálogo aún lista la herramienta como pendiente pese a la implementación y la integración frontend observadas; revisar el estado de gobernanza. Resolver el rastreo de `netops.db` en Git mediante autorización aparte. El formato de `device_type` no tiene enum ni validación de dominio observados.
