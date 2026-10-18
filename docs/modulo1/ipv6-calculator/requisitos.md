# Requisitos — Calculadora IPv6

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 1, herramienta 5.
- **Estado:** Pertenece al MVP; todavía está pendiente de implementación e integración frontend.
- **Propósito:** Calcular información de una dirección y un prefijo IPv6, incluida la red, la última dirección del bloque, la cantidad de direcciones y las clasificaciones registradas aplicables.
- **Familia admitida:** IPv6.
- **Entrada v1:** Un CIDR mediante el campo `cidr`.
- **Decisiones aplicables:** DEC-IPv6-01 a DEC-IPv6-07 en [`decision-log.md`](decision-log.md).

**Interpretación de "rango" en esta herramienta.** Cuando el catálogo oficial dice "dirección de red y rangos", en esta herramienta significa el par (*dirección de red del prefijo*, *última dirección matemática del bloque*). No se calculan "primer y último host utilizable" porque IPv6 no define ese concepto. El campo `last_address` representa la última dirección matemática del bloque; no es un "host utilizable" ni un "broadcast" (IPv6 no tiene broadcast).

## Incluye

- Validar una dirección CIDR IPv6 con prefijo entre `/0` y `/128`.
- Aceptar las formas IPv6 con dirección IPv4 embebida o mapeada que sean válidas según las reglas IPv6 aplicables.
- Normalizar la representación textual y calcular la red y la última dirección del prefijo.
- Detectar bits de host activos; en ese caso, calcular sobre la red normalizada, indicarlo mediante `host_bits_set` y devolver la advertencia `host_bits_normalized`.
- Devolver el total matemático de direcciones como cadena decimal para conservar exactamente valores de hasta `2^128` en clientes JavaScript.
- Clasificar la dirección usando una tabla curada y versionada de registros IANA pertinentes. La herramienta no debe depender de consultas de red para clasificar.
- Rechazar identificadores de zona, por ejemplo `%eth0`, con el error `zone_id_not_supported`.
- Traducir errores de dominio mediante el handler común, sin construir respuestas HTTP en el dominio ni añadir traducciones particulares en la ruta.

## No incluye en v1

- Cálculo inverso por cantidad de hosts.
- Entrada separada mediante `address` + `netmask`.
- Aceptar una dirección IPv4 no representada como una dirección IPv6 válida.
- Determinar si una dirección es alcanzable, está anunciada o es pública en una red concreta.
- Distinguir direcciones anycast a partir del texto de la dirección. Según RFC 4291, anycast se asigna desde espacio unicast y no es sintácticamente distinguible de unicast; la herramienta no puede inferir esta propiedad solo por la representación textual.
- Consultar IANA en tiempo real.

Las formas de entrada o modos adicionales podrán reconsiderarse en una v2; no forman parte del contrato v1.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| IPV6-F-001 | Aceptar una entrada CIDR IPv6 | `cidr` contiene una dirección IPv6 y un prefijo `/0`–`/128` | Resultado con dirección, longitud de prefijo, red y última dirección | APROBADO |
| IPV6-F-002 | Normalizar la representación y los bits de host | CIDR IPv6 válido; puede contener bits de host activos | `address` y campos derivados en forma canónica; `host_bits_set` indica el caso | APROBADO |
| IPV6-F-003 | Advertir la normalización | La entrada tiene bits de host activos | `warnings` contiene `{code: "host_bits_normalized", message: texto en español}` | APROBADO |
| IPV6-F-004 | Rechazar zone IDs | La parte de dirección contiene un identificador `%zona` | Error `zone_id_not_supported`, HTTP 422 | APROBADO |
| IPV6-F-005 | Aceptar IPv4 embebida/mapeada dentro de una dirección IPv6 válida | CIDR usa una forma IPv6 reconocida con representación IPv4 | Se procesa como IPv6, sin convertir la respuesta a IPv4 | APROBADO |
| IPV6-F-006 | Devolver cantidad exacta de direcciones | Prefijo válido | `total_addresses` contiene el entero matemático como cadena decimal | APROBADO |
| IPV6-F-007 | Clasificar mediante registros IANA curados | Dirección IPv6 válida | `classifications` contiene las entradas aplicables de la tabla versionada; puede estar vacía | APROBADO; catálogo exacto debe verificarse al implementar |
| IPV6-F-008 | Rechazar CIDR inválido | Falta el separador CIDR o la parte de dirección no es IPv6 válida | Error `invalid_cidr`, HTTP 422 | APROBADO |
| IPV6-F-009 | Rechazar prefijo inválido | El sufijo del prefijo no es entero o está fuera de `/0`–`/128` | Error `invalid_prefix`, HTTP 422 | APROBADO |
| IPV6-F-010 | Mantener entrada v1 única | JSON contiene solo `cidr` | No se ofrece `address` + `netmask` ni modo inverso | APROBADO |

**Formas textuales aceptadas (IPV6-F-001).** La entrada acepta cualquier representación textual válida según RFC 4291: forma comprimida (`2001:db8::1`), forma expandida (`2001:0db8:0000:0000:0000:0000:0000:0001`), forma mixta, mayúsculas o minúsculas. La salida se canonicaliza según RFC 5952.

**Datos derivados en v1.** Los campos que devuelve la herramienta son exactamente: `input`, `address`, `prefix_length`, `network`, `last_address`, `total_addresses`, `host_bits_set`, `classifications` y `warnings`, según se definen en `api-contracts.md`. Esta es la lista cerrada de "datos derivados" para v1; cualquier campo adicional requiere una decisión nueva.

**Cobertura mínima de clasificación (IPV6-F-007).** La tabla curada de IANA debe cubrir al menos los siguientes prefijos: `::/128` (unspecified), `::1/128` (loopback), `fe80::/10` (link-local), `fc00::/7` (Unique Local), `ff00::/8` (multicast) y `2001:db8::/32` (documentation). Cualquier otro prefijo del registro IANA es opcional en v1. La fecha de referencia y la URL de la consulta al registro se registran en el `decision-log.md` antes de implementar; los registros IANA pueden cambiar.

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| IPV6-NF-001 | Precisión | Los cálculos abarcan el espacio IPv6 completo y no convierten el total a número de punto flotante en JavaScript | `/0` produce exactamente `"340282366920938463463374607431768211456"` | APROBADO |
| IPV6-NF-002 | Separación | El dominio no depende de FastAPI, HTTP ni del navegador | Cálculo y clasificación se pueden invocar sin transporte HTTP | APROBADO como principio arquitectónico |
| IPV6-NF-003 | Offline | La clasificación usa datos locales curados, no llamadas a IANA en cada solicitud | La herramienta calcula sin conectividad externa | APROBADO como criterio de diseño derivado de la fuente curada |
| IPV6-NF-004 | Errores | Los mensajes dirigidos a usuario se expresan en español y no filtran datos internos | Contratos de error comunes y mensajes específicos comprobados | APROBADO |
| IPV6-NF-005 | Recursos | La solicitud procesa una sola dirección CIDR y la clasificación consulta un conjunto acotado de prefijos | No se generan enumeraciones de las direcciones de una red | APROBADO como criterio de diseño |

## Criterios de aceptación

- `{"cidr":"2001:db8::/64"}` produce red `2001:db8::`, última dirección `2001:db8::ffff:ffff:ffff:ffff` y total decimal `"18446744073709551616"`.
- `/0` y `/128` funcionan y sus cantidades son exactamente `2^128` y `1`, respectivamente.
- Una dirección válida con bits de host activos se normaliza y emite `host_bits_normalized`.
- Un zone ID se rechaza antes de procesar la dirección y produce `zone_id_not_supported`.
- CIDR y prefijo inválidos producen respectivamente `invalid_cidr` e `invalid_prefix`; ambos se traducen a HTTP 422 por el handler común.
- La API acepta solo el campo `cidr` en v1 y responde en el endpoint aprobado.
- La clasificación declara la coincidencia con los registros curados; no afirma que una dirección sea alcanzable o enrutable en el contexto local.
- Las direcciones `::`, `::1`, `fe80::1`, `fc00::1`, `ff02::1` y `2001:db8::1` (esta última con `/64`) se procesan sin error. Su clasificación coincide con la tabla curada: `::` → unspecified, `::1` → loopback, `fe80::/10` → link-local, `fc00::/7` → Unique Local, `ff00::/8` → multicast, `2001:db8::/32` → documentation.

## Fuentes y pendientes

- [IANA IPv6 Address Space](https://www.iana.org/assignments/ipv6-address-space) y [IANA IPv6 Special-Purpose Address Space](https://www.iana.org/assignments/iana-ipv6-special-registry) son fuentes de clasificación. La tabla que se implemente deberá registrar versión/fecha de extracción y referencias de cada rango.
- [RFC 4291](https://www.rfc-editor.org/rfc/rfc4291.html) describe la arquitectura de direccionamiento IPv6 y las formas de dirección con IPv4 embebida; [RFC 5952](https://www.rfc-editor.org/rfc/rfc5952.html) recomienda la representación textual canónica.
- No se define aquí un indicador booleano «pública»/«privada»: esa simplificación no refleja todas las categorías registradas.
- La selección final de rangos, nombres y códigos de clasificación debe contrastarse con los registros IANA al implementar; los registros pueden cambiar.
