# Requisitos — Calculadora MTU y fragmentación

> Estado: alcance aprobado para la herramienta 20. El catálogo fundacional la marca pendiente de desarrollo e integración; este documento no afirma que esté implementada.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 4, herramienta 20.
- **Propósito:** calcular el espacio disponible para datos a partir de un MTU y los tamaños de las cabeceras IP, transporte y túnel seleccionadas.
- **Incluye:** cálculo local de cabeceras para IPv4/IPv6, TCP/UDP y las opciones de túnel `none`, `gre`, `ipsec` y `wireguard`; informar resultado y advertencias.
- **No incluye:** medir el MTU real de una ruta, enviar paquetes, cambiar la configuración de red ni detectar automáticamente encapsulaciones.
- **Familias/protocolos admitidos:** IPv4, IPv6, TCP y UDP.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| MTU-F-001 | Aceptar un MTU entero. | `mtu`, default `1500`, mínimo `576`, máximo `9000`. | El dominio calcula con el valor validado; el valor omitido se trata como `1500`. | Aprobado |
| MTU-F-002 | Seleccionar versión IP, transporte y túnel. | `ip_version`: `ipv4` o `ipv6`; `transport`: `tcp` o `udp`; `tunnel`: `none`, `gre`, `ipsec` o `wireguard`. | Los tamaños de cabecera usados corresponden a la selección. | Aprobado; tamaños de túnel pendientes de especificación |
| MTU-F-003 | Devolver el espacio de datos y los tamaños de cabecera. | Request válido. | Respuesta incluye `mss`, `ip_header_size`, `transport_header_size` y `tunnel_header_size`. | Aprobado; semántica de `mss` para UDP pendiente |
| MTU-F-004 | Informar advertencias del cálculo. | MTU bajo o cálculo que resulte negativo, según las reglas finales. | `warnings` es un array de mensajes. | Aprobado; reconciliar advertencia de MTU <576 con mínimo de entrada |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| MTU-NF-001 | Arquitectura | El cálculo del dominio es puro y no consulta base de datos, red ni sistema operativo. | El resultado depende solo de los parámetros validados y las reglas documentadas. | Aprobado |
| MTU-NF-002 | Concurrencia | La capa API usa `asyncio.Semaphore(5)`. | Las solicitudes pasan por el semáforo de cinco permisos. | Aprobado; conducta de saturación pendiente |

## Criterios de aceptación

- Omitir `mtu` equivale a usar `1500`; valores menores que `576`, mayores que `9000` o no enteros se rechazan conforme al contrato que se defina.
- Se admiten únicamente los valores enumerados para `ip_version`, `transport` y `tunnel`.
- La respuesta incluye tamaños en bytes, el resultado de datos y `warnings`.
- El cálculo no ejecuta comandos ni requiere conectividad externa.
- Antes de implementar se define qué representa `mss` para UDP y los tamaños de overhead de cada túnel.

## Fuentes y pendientes

- **Decisiones aplicables:** [MTU-DEC-01 y MTU-DEC-02](decision-log.md).
- **Fuente de alcance:** [catálogo fundacional, herramienta 20](../../fundacional/catalogo.md).
- **Fuentes técnicas:** [RFC 6691 — TCP Options and Maximum Segment Size](https://www.rfc-editor.org/rfc/rfc6691.html); [RFC 768 — User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768.html).
- **Pendiente de aprobación o investigación:** semántica de `mss` con UDP; tamaños y perfiles de overhead GRE/IPsec/WireGuard; si `mtu` es MTU interior o exterior; política de valores negativos; advertencia `<576` frente al mínimo validado de `576`; errores HTTP y comportamiento al saturarse el semáforo.
