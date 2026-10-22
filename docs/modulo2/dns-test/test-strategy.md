# Estrategia de pruebas — Diagnóstico DNS

## Estado

Estrategia para la futura implementación; ninguna prueba DNS se declara implementada o ejecutada en este documento. El catálogo mantiene la herramienta pendiente de desarrollo e integración.

## Principios

- Las pruebas unitarias usan `FakeDnsRunner` y respuestas controladas.
- Las pruebas HTTP sustituyen el runner; no realizan consultas a Internet.
- Las pruebas del adaptador simulan la biblioteca dnspython o usan un servidor DNS local aislado, si se autoriza y resulta necesario.
- Los resultados esperados deben derivarse de fixtures independientes, no de consultar un resolver público durante CI.

## Matriz de pruebas de dominio

| Caso | Preparación | Resultado esperado |
|---|---|---|
| Cada tipo permitido | Casos A, AAAA, MX, TXT, NS y CNAME | Se envía al runner el tipo normalizado permitido. |
| Tipo no admitido | AAA, SRV, valor en blanco o casing no permitido según contrato | Error de validación; runner no invocado. |
| Dominio válido | Nombre de dominio conforme a la política aprobada | Llamada correcta al runner. |
| URL y entradas hostiles | Esquema, path, query, fragmento, espacios, controles o credenciales | Rechazo previo a la consulta. |
| Resolver omitido | `resolver` ausente | Runner configura uso de DNS del sistema. |
| Resolver explícito | IPv4 y, si se admite, IPv6 literal | Runner recibe el nameserver pedido. |
| Resolver inválido | Nombre, URL o dirección mal formada | Error de validación antes de consultar. |
| MX | Respuesta controlada con preferencia y exchange | Cadena `"<prioridad> <servidor>"`, como `"10 smtp.google.com"`. |
| Otros registros | Rdata representativos por tipo | Conversión a strings según el formato estable aprobado. |
| NXDOMAIN | Runner informa respuesta NXDOMAIN | `status == "nxdomain"`, sin confundir con error de validación. |
| Falla DNS | Timeout, SERVFAIL, NoNameservers y NoAnswer simulados | `status == "error"` con distinción interna preservada; respuesta HTTP depende de DNS-PEND-004. |

## Matriz de API

- Solicitud válida para cada `record_type`; verificar forma exacta de la respuesta y el caso MX documentado.
- Resolver omitido y explícito; comprobar el valor de respuesta cuando el contrato cierre DNS-PEND-002.
- Dominio/URL inválidos, tipo no admitido y resolver inválido: comprobar status y códigos acordados para el Módulo 2.
- NXDOMAIN debe conservar el estado diagnóstico y seguir el status que se apruebe en DNS-PEND-004.
- Timeout total superior a 5 segundos: comprobar terminación dentro del límite y status/error contractual.
- Saturación del semáforo de 10: comprobar el comportamiento que se apruebe en DNS-PEND-005.
- Tipo de contenido incorrecto, JSON malformado y error inesperado: comprobar el contrato transversal cuando se formalice.

## Adaptador e integración

- Verificar construcción de `dns.resolver.Resolver` con configuración del sistema cuando no se entrega resolver.
- Verificar configuración de `nameservers` cuando se indica una IP.
- Simular una respuesta de cada tipo y comprobar serialización de A/AAAA, MX, TXT, NS y CNAME.
- Simular NXDOMAIN, NoAnswer, NoNameservers y LifetimeTimeout; comprobar su clasificación interna.
- Verificar el límite de vida total de cinco segundos para intentos/reintentos.
- Confirmar que la llamada síncrona no bloquea el event loop y que cancelar o expirar la solicitud no deja trabajo sin límite.

## Recursos y seguridad

- Confirmar que solo se realizan consultas para los seis tipos permitidos.
- Confirmar que las URLs y entradas con datos extraños no alcanzan el runner.
- Comprobar liberación del semáforo en éxito, NXDOMAIN, timeout y excepciones.
- Verificar concurrencia con el número de workers documentado; no afirmar alcance global a partir de un semáforo por proceso.
- No usar credenciales ni registrar datos sensibles de consultas.

## Datos esperados independientes

Las pruebas unitarias deben usar fixtures DNS declarados y revisables. Los ejemplos públicos (por ejemplo, google.com) son ilustrativos del contrato, no dependencias de la suite ni valores que deban consultarse en tiempo de prueba. La validación de nombres debe usar casos de prueba derivados de la política normativa que se apruebe; la serialización esperada se verifica contra estructuras de respuesta controladas.

## Referencias

- [Requisitos](requisitos.md).
- [Arquitectura](arquitectura.md).
- [Contrato de API](api-contracts.md).
- [Estrategia de pruebas de Ping](../ping/test-strategy.md).
- [Estrategia de pruebas de Traceroute](../traceroute/test-strategy.md).
- [Estrategia de pruebas de TCP Test](../tcp-test/test-strategy.md).
