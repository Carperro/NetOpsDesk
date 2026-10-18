# Arquitectura — Calculadora IPv6

## Estado

Este documento describe la arquitectura objetivo aprobada para la herramienta 5. A fecha 2026-10-18 no hay implementación IPv6 en `src/` ni pruebas de IPv6 en `tests/`; los archivos y responsabilidades siguientes son destino de implementación, no componentes existentes.

## Componentes propuestos para la implementación

- **Dominio:** `src/netops_desk/ipv6.py` contendrá el cálculo puro de CIDR IPv6, la normalización, el cálculo de red/última dirección, la conversión decimal exacta del total y la clasificación mediante datos locales curados. No importará FastAPI, Pydantic ni módulos del navegador.
- **Modelos de API:** `src/netops_desk/api/models/ipv6.py` validará la forma de entrada y definirá el esquema de respuesta. La entrada v1 contiene `cidr`; los modelos de API no duplicarán el cálculo del dominio.
- **Ruta:** `src/netops_desk/api/routes/ipv6.py` declarará un `APIRouter` sin `prefix` y la ruta completa `POST /api/v1/tools/ipv6/calculate`. Comprobará `Content-Type` mediante `require_json_content_type`, adaptará el modelo a la llamada de dominio y dejará que `DomainError` ascienda al handler global.
- **Errores:** `src/netops_desk/api/exceptions.py` ya registra `domain_error_handler`. La ruta IPv6 no debe traducir los tres errores de dominio a respuestas HTTP por cuenta propia.
- **Aplicación:** `src/netops_desk/api/main.py` incluirá el router cuando se autorice implementar la herramienta. La ruta de página se añadirá junto con la integración frontend.
- **Frontend:** la página futura pertenecerá a `src/netops_desk/static/tools/ipv6.html` y su interacción a `src/netops_desk/static/js/ipv6.js`, manteniendo HTML/CSS/JavaScript vanilla y usando el formateador común de errores. El total se conservará como texto decimal; no se parseará a `Number`.
- **Pruebas:** la futura cobertura de dominio y API se organizará en `tests/test_ipv6_domain.py` y `tests/test_api_ipv6.py`. Las guardas estáticas de la página IPv6 (uso de `textContent`, no interpolación de datos dinámicos, uso del formateador común de errores) se agregan en `tests/test_frontend_static.py`, siguiendo los patrones ya existentes para IPv4, Subnetting, VLSM y Overlap. Esta tarea no crea ninguno de esos archivos.

## Flujo de solicitud

1. El cliente envía JSON con el campo `cidr` al endpoint aprobado.
2. FastAPI valida tipo y estructura del cuerpo; la dependencia común verifica el tipo MIME.
3. La ruta invoca el dominio con la cadena CIDR. El dominio rechaza zone IDs, valida dirección/prefijo, calcula la red y demás valores, determina si se normalizaron bits de host y consulta la tabla local de clasificación. El dominio trata las direcciones IPv4-embedded/mapped (`::ffff:0:0/96` y rangos análogos) como IPv6 puro: no convierte la respuesta a IPv4, no cambia el cálculo, y solo las clasifica según la tabla IANA cuando corresponda. El dominio conserva la cadena CIDR original y la incluye en la respuesta como `input`, sin canonicalizarla; los campos derivados (`address`, `network`, etc.) sí se canonicalizan según RFC 5952.
4. El dominio devuelve datos o lanza `DomainError` con uno de los códigos definidos. No asigna estados HTTP.
5. El modelo de respuesta valida el resultado y mantiene `total_addresses` como cadena decimal.
6. El handler global traduce errores de dominio a HTTP 422 y al sobre JSON común.
7. El frontend muestra valores dinámicos como texto y conserva exactamente la cadena decimal devuelta.

### Caminos de error (verificados por `tests/test_api_ipv6.py`)

- `415` si `Content-Type` no es `application/json` (dependencia común `require_json_content_type`).
- `400` `invalid_json` si el cuerpo no se puede leer o decodificar (DEC-007).
- `422` `unknown_field`, `missing_field` o `invalid_type` si la validación Pydantic falla.
- `422` `invalid_cidr`, `invalid_prefix` o `zone_id_not_supported` si el dominio rechaza (traducido por `domain_error_handler`).
- `500` `internal_error` si algo inesperado falla.

## Límites y datos de clasificación

**Estructura de la tabla curada.** La tabla se implementa como una constante a nivel de módulo. Cada entrada registra: el prefijo en notación CIDR, la etiqueta estable que aparece en `classifications`, la fuente registral (IANA o RFC). La tabla global registra una sola fecha de extracción IANA. Si la tabla vive en `ipv6.py` o en un módulo auxiliar (`ipv6_registry.py`) se decide al implementar y se documenta en `decision-log.md`.

- La operación recibe una sola cadena CIDR; no necesita una capa de servicio adicional mientras no exista coordinación con persistencia u otros casos de uso.
- El dominio no materializa las direcciones contenidas por la red. Red, última dirección y total se obtienen mediante operaciones aritméticas sobre enteros IPv6.
- Los rangos IANA se mantendrán en datos locales, acotados y revisables, con referencias y fecha de actualización. No se consultarán registros externos durante cada cálculo.
- La clasificación es una descripción de registro. No equivale a garantía de conectividad, asignación a un usuario, anuncio BGP ni alcanzabilidad local.
- La precedencia de coincidencias se resolverá por prefijo más específico dentro del catálogo versionado. Si fuentes registrales diferentes producen atributos que no se pueden ordenar por especificidad, se conservarán como entradas distintas en vez de combinarlas en una etiqueta «pública/privada».
- **Caso sin coincidencia.** Si ninguna entrada de la tabla coincide con la dirección, `classifications` se devuelve como lista vacía. La herramienta no fuerza una clasificación de respaldo como "global" o "pública": la ausencia de coincidencia es un resultado legítimo.
- **Solapamiento con igual longitud de prefijo.** Si dos entradas de la tabla coinciden con la misma longitud de prefijo, se conservan ambas etiquetas en `classifications` en el orden en que aparecen en la tabla. El diseño de la tabla debe evitar este caso; se verifica al construir la tabla, no en tiempo de cálculo.
- **Justificación de tabla propia frente a `ipaddress`.** La tabla curada no delega en las propiedades de `ipaddress` (`is_private`, `is_global`, etc.) porque (a) su semántica puede diferir del registro IANA especial, (b) pueden cambiar entre versiones de Python sin aviso en el contrato, y (c) no distinguen categorías que el registro IANA sí separa (por ejemplo, documentation vs. private-use). La tabla local es la fuente de verdad para la clasificación; `ipaddress` se usa solo para parseo, canonicalización y aritmética.
- **Anycast no clasificable.** La tabla no incluye una categoría "anycast": RFC 4291 establece que anycast no es sintácticamente distinguible de unicast. Cualquier dirección que según RFC podría usarse para anycast se clasifica según su prefijo; la condición de "ser anycast" no es observable desde el texto.

## Seguridad, errores y recursos

- Rechazar zone IDs evita incorporar una identidad de interfaz local cuyo significado depende del sistema y del contexto.
- Los mensajes públicos se mantienen en español. El handler común no revela trazas; registra los fallos en el servidor.
- Las rutas no duplican validación de dominio ni transforman excepciones en códigos HTTP locales.
- El tamaño de trabajo debe depender de la longitud de la entrada y del número fijo de prefijos de la tabla, nunca del número de direcciones de la red.
- La página no debe convertir `total_addresses` a `Number`, porque IPv6 puede exceder `Number.MAX_SAFE_INTEGER`.

## Referencias

- Arquitectura de referencia: [`../ipv4-calculator/arquitectura.md`](../ipv4-calculator/arquitectura.md) y [`../ipv4-calculator/api-contracts.md`](../ipv4-calculator/api-contracts.md).
- Convenciones HTTP compartidas: [`../api-contracts.md`](../api-contracts.md).
- Fuentes para direcciones y clasificación: [RFC 4291](https://www.rfc-editor.org/rfc/rfc4291.html), [RFC 5952](https://www.rfc-editor.org/rfc/rfc5952.html), [IANA IPv6 Address Space](https://www.iana.org/assignments/ipv6-address-space) e [IANA IPv6 Special-Purpose Address Registry](https://www.iana.org/assignments/iana-ipv6-special-registry).
