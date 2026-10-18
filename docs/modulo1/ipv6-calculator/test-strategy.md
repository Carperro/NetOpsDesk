# Estrategia de pruebas — Calculadora IPv6

## Estado y alcance

La estrategia define verificaciones objetivo derivadas de los requisitos y el contrato. La herramienta no está implementada: no existen actualmente archivos de pruebas IPv6 y ninguno de los casos siguientes se considera implementado o ejecutado. La suite general existente puede pasar sin validar el comportamiento IPv6.

| Capa | Archivo(s) objetivo | Qué debe verificar | Estado |
|---|---|---|---|
| Dominio | `tests/test_ipv6_domain.py` | Validación, normalización, aritmética de límites, precisión decimal y clasificación | Pendiente de implementación |
| API | `tests/test_api_ipv6.py` | Ruta, esquemas, códigos HTTP, envelope común y traducción de `DomainError` | Pendiente de implementación |
| Interfaz estática | `tests/test_frontend_static.py` (extensión autorizada junto a la implementación) | Carga de recursos, campos, mensajes y protección de salida | Pendiente de implementación |
| Navegador | Prueba de navegador si se incorpora/autoriza esa capa | Flujo visual, carga, error, normalización y presentación exacta del total | Pendiente; no asumir automatización |

## Matriz de casos previstos

| Caso | Entrada | Resultado esperado | Prueba objetivo | Estado |
|---|---|---|---|---|
| Prefijo `/0` | `::/0` | Red `::`, última `ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff`, total `"340282366920938463463374607431768211456"` | Dominio | Pendiente |
| Prefijo `/128` | `2001:db8::1/128` | Una dirección; total `"1"` | Dominio | Pendiente |
| Dirección no especificada | `::/128` | Entrada válida y clasificación correspondiente según catálogo curado | Dominio | Pendiente |
| Representación comprimida y canónica | `2001:0DB8:0:0::1/128` | Dirección de salida canónica en minúsculas y forma comprimida | Dominio/API | Pendiente |
| Representación expandida | `2001:0db8:0000:0000:0000:0000:0000:0001/128` | Entrada válida; salida canonicalizada según RFC 5952 | Dominio | Pendiente |
| Dirección en mayúsculas | `2001:DB8::/64` | Entrada válida; salida en representación canónica minúscula | Dominio | Pendiente |
| Bits de host activos | `2001:db8::1/64` | `host_bits_set=true`, red `2001:db8::`, warning `host_bits_normalized`; `address` conserva `::1` | Dominio/API | Pendiente |
| Sin bits de host activos | `2001:db8::/64` | `host_bits_set=false`; no incluye warning `host_bits_normalized` | Dominio/API | Pendiente |
| IPv4-mapped | `::ffff:192.0.2.1/128` | Aceptada como IPv6 y representada como tal | Dominio/API | Pendiente |
| IPv4-embedded de mecanismo definido | Forma válida según RFC 6052 | Se procesa con la semántica IPv6 y no como IPv4 aislada | Dominio | Pendiente |
| Zone ID | `fe80::1%eth0/64` | `DomainError` `zone_id_not_supported`, respuesta API 422 | Dominio/API | Pendiente |
| Dirección malformada | `not-an-ip/64` | `invalid_cidr`, HTTP 422 | Dominio/API | Pendiente |
| CIDR sin `/` | `2001:db8::1` | `invalid_cidr`, HTTP 422 | Dominio/API | Pendiente |
| CIDR con doble `/` | `2001:db8::1/64/1` | `invalid_prefix`, HTTP 422 | Dominio/API | Pendiente |
| IPv4 como entrada completa | `192.168.1.1/24` | `invalid_cidr`, HTTP 422 | Dominio/API | Pendiente |
| Prefijo inválido | `/129`, `/-1`, `/abc` | `invalid_prefix`, HTTP 422 | Dominio/API | Pendiente |
| Total exacto `/0` | `::/0` | Cadena decimal `"340282366920938463463374607431768211456"`, no entero JSON | Dominio/API/frontend | Pendiente |
| Total exacto `/64` | `2001:db8::/64` | Cadena decimal `"18446744073709551616"`, no entero JSON | Dominio/API/frontend | Pendiente |
| Total exacto `/128` | `2001:db8::1/128` | Cadena decimal `"1"`, no entero JSON | Dominio/API/frontend | Pendiente |
| Clase especial documentada | `2001:db8::1/128` | Coincidencia con el registro IANA de documentación y referencia al prefijo | Dominio | Pendiente |
| Loopback, link-local, multicast, ULA | Ejemplos representativos de cada prefijo registrado | Códigos/nombres coinciden con la tabla curada y no con heurísticas inventadas | Dominio | Pendiente |
| Clasificación unspecified | `::/128` | Coincide con `::/128` (unspecified) | Dominio | Pendiente |
| Clasificación loopback | `::1/128` | Coincide con `::1/128` (loopback) | Dominio | Pendiente |
| Clasificación link-local | `fe80::/10` | Coincide con `fe80::/10` (link-local) | Dominio | Pendiente |
| Clasificación Unique Local | `fc00::/7` | Coincide con `fc00::/7` (Unique Local) | Dominio | Pendiente |
| Clasificación multicast | `ff00::/8` | Coincide con `ff00::/8` (multicast) | Dominio | Pendiente |
| Clasificación documentation | `2001:db8::/32` | Coincide con `2001:db8::/32` (documentation) | Dominio | Pendiente |
| Sin coincidencia de clasificación | Una dirección cuyo prefijo no está incluido en la tabla curada | `classifications: []` | Dominio | Pendiente |
| Prefijo válido con entradas extra | JSON incluye `address` además de `cidr` | HTTP 422 con código común `unknown_field` | API | Pendiente |
| Entrada sin campo | `{}` | HTTP 422 con sobre común | API | Pendiente |
| Tipo de contenido incorrecto | `text/plain` | HTTP 415 `unsupported_media_type` | API | Pendiente |
| Cuerpo ilegible/malformado | Bytes JSON ilegibles o sintaxis JSON inválida | HTTP 400/422 según distinción contractual de DEC-007 | API | Pendiente |
| Ruta o método incorrectos | Ruta inexistente o método distinto de POST | HTTP 404/405 y sobre común | API | Pendiente |
| Fallo inesperado | Excepción no controlada inducida en prueba aislada | HTTP 500 `internal_error`, detalle genérico sin traza | API | Pendiente |
| Representación de errores en interfaz | Respuestas 4xx/5xx y pérdida de conexión | Mensaje pertinente en español; no muestra trazas ni texto técnico del navegador | Frontend | Pendiente |

Las guardas estáticas en `tests/test_frontend_static.py` deben verificar que `static/js/ipv6.js` usa `textContent` y no `innerHTML` con datos dinámicos, que usa el formateador común `static/js/api-errors.js`, que `total_addresses` no se convierte con `Number(...)`, `parseInt` o `parseFloat`, y que `static/tools/ipv6.html` carga `sidebar.js` y `common.js` como las demás herramientas.

## Invariantes y oráculos

- Para cada CIDR válido, `network` pertenece al prefijo normalizado, `last_address` es su última dirección y la cantidad satisface `total_addresses = 2^(128-prefix_length)`.
- `total_addresses` debe compararse como cadena decimal exacta, especialmente para `/0`, `/64` y `/128`.
- Si `host_bits_set` es verdadero, la red se calcula con los bits de host en cero y hay exactamente una advertencia `host_bits_normalized`; en caso contrario, no se informa esa advertencia.
- Los vectores de clasificación deben citar la versión/fecha de la tabla curada y el registro IANA de origen. No usar el resultado de una biblioteca como único oráculo para categorías de registro.
- Las fuentes independientes para validar resultados esperados son: RFC 5952 para la canonicalización; `ipaddress` de la biblioteca estándar como oráculo auxiliar, nunca único; cálculo manual de `2^(128-prefix_length)` para los totales; y el IANA IPv6 Special-Purpose Address Registry para las clasificaciones. La fecha de extracción del registro se fija en `decision-log.md` al implementar la tabla.
- Ninguna prueba debe enumerar las direcciones de un prefijo; los casos `/0` y `/64` deben ejecutarse con operaciones aritméticas acotadas.
- Los errores `invalid_cidr`, `invalid_prefix` y `zone_id_not_supported` deben nacer como errores de dominio y llegar a HTTP 422 por el handler global.

## Ejecución y última verificación

- **Comando de regresión existente:** `.\.venv\Scripts\python.exe -m pytest tests/ -q`
- **Fecha de la verificación de regresión:** 2026-10-18.
- **Resultado de la suite existente:** 170 pruebas aprobadas, 0 fallidas y 0 omitidas (`170 passed in 1.12s`). Esta ejecución valida la regresión del repositorio, pero no el comportamiento IPv6.
- **Pruebas IPv6:** ninguna implementada ni ejecutada; no hay módulos IPv6 ni pruebas IPv6 creados en esta tarea.
- **Verificación dinámica de navegador:** no realizada ni autorizada por esta tarea.
- **Pendientes:** implementar dominio/API/frontend y las pruebas correspondientes solo mediante autorización posterior; revisar la tabla IANA y registrar su versión antes de cerrar pruebas de clasificación.
