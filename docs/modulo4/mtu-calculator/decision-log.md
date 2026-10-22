# Registro de decisiones — Calculadora MTU y fragmentación

Este registro recoge el alcance aprobado para la herramienta 20 y separa las definiciones aún pendientes. La existencia de estos documentos no implica implementación.

## Decisiones aprobadas

### MTU-DEC-01 — Cálculo local de cabeceras

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** La herramienta calcula el espacio disponible para datos en función de un MTU y de protocolos/encapsulaciones seleccionados.
- **Decisión:** Implementar el dominio puro en `netops_desk/mtu_calculator.py`; no requiere base de datos, red ni `subprocess`. La API llama al dominio y devuelve el resultado.
- **Motivo:** Mantener el cálculo determinista y separado del transporte HTTP y de efectos externos.
- **Alternativas:** No registradas.
- **Consecuencias:** Las reglas y perfiles de cabecera deben estar especificados y probados antes de considerar el cálculo completo.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 20.

### MTU-DEC-02 — Entradas y concurrencia

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Definir los parámetros admitidos y limitar llamadas concurrentes a la operación.
- **Decisión:** `mtu` entero default 1500, mínimo 68 y máximo 9000; `ip_version` acepta `ipv4`/`ipv6`; `transport` acepta `tcp`/`udp`; `tunnel` acepta `none`/`gre`/`ipsec`/`wireguard`. La capa API usará `asyncio.Semaphore(5)`. Si `mtu < 576`, agregar `mtu_below_minimum`.
- **Motivo:** Ofrecer un conjunto de opciones acotado y validable.
- **Alternativas:** No registradas.
- **Consecuencias:** La acción al agotarse el semáforo no fue especificada; no se da por aprobado un status HTTP ni una política de workers. La aplicabilidad del rango 68–1279 a IPv6 queda sujeta a la salvedad técnica registrada en MTU-PEND-01.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 20.

### MTU-DEC-03 — MTU de enlace y perfiles fijos de túnel

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** El cálculo necesitaba una referencia de MTU y overhead determinista para cada túnel disponible.
- **Decisión:** `mtu` representa el máximo de bytes del paquete IP que admite el enlace (por ejemplo, 1500 para Ethernet, sin contar la cabecera Ethernet). Usar overhead total fijo: `none` 0 bytes; `gre` 24 bytes (IPv4 exterior 20 + GRE 4); `ipsec` 60 bytes (IPv4 exterior 20 + ESP/Auth 40); `wireguard` 60 bytes (IPv4 exterior 20 + UDP 8 + WireGuard 32). Estos perfiles fijan IPv4 exterior.
- **Motivo:** Hacer reproducibles los cálculos sin añadir opciones variables a la entrada.
- **Alternativas:** Overhead dinámico según modo, opciones o algoritmos; no seleccionado para los perfiles iniciales.
- **Consecuencias:** Los valores representan perfiles fijos del producto, no todas las configuraciones posibles. GRE usa cabecera base sin checksum/opciones adicionales; IPsec usa el overhead ESP/Auth fijo aprobado; no se contempla encapsulación exterior IPv6 en estos perfiles.
- **Aprobación:** Resolutivo explícito del usuario sobre los perfiles de túnel.

### MTU-DEC-04 — Payload común y resultado no negativo

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** La API admite TCP y UDP, aunque MSS es terminología específica de TCP; el overhead puede superar el MTU.
- **Decisión:** Conservar el campo `mss` por compatibilidad y definirlo como payload máximo de datos: MSS para TCP y datos máximos para UDP. Calcular `max(0, mtu - ip_header_size - transport_header_size - tunnel_header_size)`. Si el total de cabeceras excede el MTU, devolver `mss: 0` y agregar `packet_too_small`, sin error HTTP.
- **Motivo:** Mantener un campo común de resultado y representar la falta de espacio como advertencia recuperable.
- **Alternativas:** Un campo distinto para UDP o error HTTP ante resultado negativo; no seleccionados.
- **Consecuencias:** La documentación y la interfaz deben aclarar que `mss` con UDP es un nombre de campo compatible, no el MSS TCP definido protocolariamente.
- **Aprobación:** Resolutivo explícito del usuario sobre semántica de `mss` y resultados negativos.

### MTU-DEC-05 — Rango y advertencia de MTU bajo

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** El mínimo previo de 576 impedía emitir la advertencia solicitada para valores inferiores.
- **Decisión:** La validación acepta `mtu` de 68 a 9000; cuando `mtu < 576`, agrega `mtu_below_minimum`. El valor 68 se adopta como límite inferior del producto tomando como referencia que RFC 791 requiere poder reenviar un datagrama de 68 octetos sin fragmentarlo nuevamente.
- **Motivo:** Permitir que la advertencia diferencie la referencia IPv4 de datagramas de 576 octetos del mínimo de entrada elegido para la herramienta.
- **Alternativas:** Mantener 576 como mínimo de validación, lo que haría inalcanzable la advertencia; descartada.
- **Consecuencias:** Se aceptan valores 68–575 con advertencia. RFC 8200 fija un MTU mínimo de enlace de 1280 para IPv6; la política de IPv6 bajo 1280 queda como pendiente separada.
- **Aprobación:** Resolutivo explícito del usuario sobre mínimo 68 y advertencia bajo 576.

## Pendientes de decisión

### MTU-PEND-01 — MTU IPv6 inferior a 1280

La validación aprobada permite valores 68–1279 para cualquier `ip_version`, pero RFC 8200 establece que cada enlace IPv6 debe soportar MTU de al menos 1280 octetos. Definir si esos valores se aceptan con una advertencia adicional, se rechazan para IPv6 o se consideran un cálculo matemático sin garantía de conformidad del enlace.

### MTU-PEND-02 — Errores HTTP y saturación

Definir códigos HTTP para entradas inválidas y conducta al agotarse `asyncio.Semaphore(5)`, conforme al contrato común del Módulo 4.
