# Requisitos del MVP - NetOps Desk

## Objetivo del MVP

Proveer una calculadora IPv4/CIDR funcional mediante una API FastAPI y una interfaz web local, con pruebas automatizadas que verifiquen el dominio, la API y la integración frontend-backend.

## Alcance incluido

- **Calculadora IPv4/CIDR**:
  - Cálculo de dirección de red, broadcast, máscara de subred, rango de hosts y cantidad de direcciones.
  - Soporte para prefijos desde /0 hasta /32.
  - Manejo de direcciones IP válidas en formato IPv4.
- **API REST**:
  - Endpoint para calcular IPv4/CIDR (`POST /api/v1/tools/ipv4/calculate`).
  - Construida con FastAPI.
  - Validación de entrada mediante Pydantic.
  - Servidor ASGI con Uvicorn.
- **Frontend**:
  - Interfaz HTML5 para cálculo directo por CIDR o address/netmask y cálculo inverso por cantidad de hosts.
  - Estilos CSS3 nativos.
  - Lógica de interacción con JavaScript vanilla (fetch API para comunicarse con el backend).
  - No depende de CDN ni recursos externos obligatorios.
- **Pruebas automatizadas**:
  - Pruebas unitarias del dominio (cálculos IPv4/CIDR).
  - Pruebas HTTP de la API con Pytest.
  - Pruebas de interfaz estática y comprobaciones HTTP de la API.
  - El requisito aprobado de integración entre frontend y API sigue siendo criterio del MVP; las pruebas actuales no simulan una interacción completa en navegador.

## Alcance excluido (no parte del MVP)

- Autenticación y gestión de usuarios.
- Persistencia de datos (SQLite, SQLAlchemy).
- Inventario de dispositivos o historial de diagnósticos.
- Herramientas de diagnóstico del sistema operativo (ping, traceroute, etc.).
- Acceso por LAN (el servidor solo escucha en `127.0.0.1`).
- Frameworks de frontend (React, Vue, etc.) o bibliotecas de estilos (Tailwind, etc.).
- Docker u otras tecnologías de contenerización.
- Herramientas adicionales del catálogo oficial (solo la calculadora IPv4/CIDR).

## Requisitos funcionales de la calculadora IPv4/CIDR

### Entrada

El cálculo directo acepta exactamente **cidr** o **address** + **netmask**; son excluyentes. No se admite **ip** + **prefix** ni compatibilidad retroactiva. **mode** directo es opcional, con valores **conventional** (default) y **point-to-point**.

El cálculo inverso requiere **required_hosts**, entero >= 1, y **mode** conventional o point-to-point. Cero no es válido. Las formas directa e inversa son excluyentes. Se rechazan campos desconocidos y combinaciones incompatibles.

### Salida directa y validación

La respuesta contiene **network**, **broadcast**, **netmask**, **wildcard**, **first_usable**, **last_usable**, **total_addresses**, **usable_addresses**, **binary**, **warnings**. **total_addresses** es tamaño del bloque; **usable_addresses** es capacidad efectiva. Warnings siempre es lista raíz de **{code, message}**.

Validar IPv4, prefijos 0–32 y máscara IPv4 contigua. Si la dirección tiene bits de host activos, normalizar a la red y emitir **host_bits_normalized**; no rechazarla solo por ello.

- Conventional: para /0–/30, capacidad = 2^(32-prefix) - 2; /31 y /32 tienen capacidad 0.
- Point-to-point: /31 capacidad 2 y /32 capacidad 1.
- Point-to-point en otros prefijos aplica conventional y emite **point_to_point_not_applicable**.

Conventional /31 y /32: **broadcast**, **first_usable** y **last_usable** son null. Point-to-point /31 y /32: broadcast null; utilizables son ambas direcciones de /31 y la única dirección de /32. No confundir último valor matemático del bloque con broadcast dedicado.

### Cálculo inverso

Evaluar prefijos /32, /31, ..., /0 y seleccionar el primero cuya capacidad efectiva >= **required_hosts**. Es el prefijo de mayor longitud que satisface la solicitud. En /0 la capacidad máxima es 4.294.967.294; superar ese valor produce HTTP 422 **insufficient_capacity**.

**mode_requested** es el modo recibido. **mode_applied** es point-to-point solo si se eligió /31 o /32 bajo ese modo; en otro caso conventional. Emitir **point_to_point_not_applicable** si se solicitó point-to-point y se eligió otro prefijo.

La respuesta inversa contiene **required_hosts**, **mode_requested**, **mode_applied**, **prefix**, **total_addresses**, **usable_addresses**, **warnings**; no contiene **network**, **binary** ni **classification**, porque no hay dirección base.

### Objeto binary

La respuesta directa contiene exactamente seis claves: **network**, **broadcast**, **netmask**, **wildcard**, **first_usable**, **last_usable**. Cada valor no nulo es cuatro octetos binarios de ocho bits separados por puntos; si el campo IPv4 es null, su valor binary también es null. La respuesta inversa no contiene binary.

### Clasificación

La clasificación de direcciones por rango (privada, pública, reservada, etc.) **no forma parte del response público inicial**. Queda deseada y aplazada hasta verificar el catálogo exacto de asignaciones IANA y el vocabulario de salida. No se inventan categorías ni prefijos.

## Requisitos no funcionales

- Los cálculos deben retornar en menos de 100 ms para cualquier entrada válida.
- El servicio opera solo en `127.0.0.1`; no se implementa autenticación en el MVP.
- Las entradas se validan en los límites del sistema mediante Pydantic (`extra="forbid"`, tipos estrictos) y el dominio (`ipaddress`, validación de máscaras contiguas). Se rechazan campos desconocidos y tipos no admitidos.
- El dominio permanece independiente de FastAPI, navegador y base de datos.
- Los supuestos de cálculo quedan documentados.

## Criterios de aceptación verificables

- Para `192.168.1.0/24`: `network=192.168.1.0`, `broadcast=192.168.1.255`, `netmask=255.255.255.0`, `first_usable=192.168.1.1`, `last_usable=192.168.1.254`, `total_addresses=256` y `usable_addresses=254`.
- Para `10.0.0.0/8`: `network=10.0.0.0`, `broadcast=10.255.255.255`, `netmask=255.0.0.0`, `total_addresses=16777216` y `usable_addresses=16777214`.
- Para `172.16.0.0/12`: `network=172.16.0.0`, `broadcast=172.31.255.255`, `netmask=255.240.0.0`, `total_addresses=1048576` y `usable_addresses=1048574`.
- La API devuelve 200 y el esquema definido para entradas válidas. Los errores incluyen HTTP 400 `invalid_json` (errores de lectura del cuerpo), 405, 415, 422 y 500, según `api-contracts.md` y `decision-log.md` (DEC-007).
- Las pruebas cubren casos normales, límites, modos y entradas inválidas; la interfaz presenta resultados, warnings y errores.

## Restricciones de operación local

- FastAPI escucha exclusivamente en `127.0.0.1`.
- El frontend se sirve desde el mismo origen y realiza llamadas a la API en ese origen.
- No se requieren permisos especiales de red o firewall.
- Las dependencias se instalan en un entorno virtual local.