# Registro de decisiones — Calculadora IPv6

Las decisiones globales se consultan en [`../../fundacional/decision-log.md`](../../fundacional/decision-log.md). Este registro contiene las decisiones específicas de la herramienta y la evidencia del contrato compartido aplicable.

## DEC-IPv6-01 — Entrada CIDR única en v1

- **Estado:** APROBADA
- **Fecha de aprobación:** 2026-10-18
- **Contexto:** La herramienta necesita una forma de entrada clara y consistente con la API IPv4 existente.
- **Decisión:** Aceptar `{"cidr":"2001:db8::/64"}` como solicitud v1.
- **Motivo:** Sigue el campo directo `cidr` utilizado por la Calculadora IPv4/CIDR y evita ambigüedad entre formas de entrada.
- **Alternativas:** `address` + `netmask`, y `ip` + `prefix`.
- **Consecuencias:** No incluir esos campos ni modo inverso en v1. Evaluarlos solo para una v2 si surge una necesidad aprobada.
- **Aprobación:** Aprobación explícita del usuario en F5, 2026-10-18.

## DEC-IPv6-02 — Normalizar bits de host y advertir

- **Estado:** APROBADA (aprobada en sesión previa)
- **Fecha de aprobación registrada:** 2026-10-18 (sesión previa, según el contexto confirmado por el usuario)
- **Contexto:** El usuario puede introducir una dirección válida que no sea la dirección de red del prefijo.
- **Decisión:** No rechazarla solo por tener bits de host activos. Calcular la red y los límites a partir del CIDR normalizado, establecer `host_bits_set` y emitir `host_bits_normalized` en `warnings`.
- **Motivo:** Mantener un flujo útil y hacer explícita la normalización al cliente.
- **Alternativas:** Rechazar la entrada o normalizarla en silencio.
- **Consecuencias:** `input` conserva el texto recibido; `address` conserva la dirección de entrada en forma canónica; `network` y `last_address` describen el bloque normalizado.
- **Aprobación:** Aprobación previa informada por el usuario; no es una propuesta nueva de esta actualización.

## DEC-IPv6-03 — Rechazar identificadores de zona

- **Estado:** APROBADA (aprobada en sesión previa)
- **Fecha de aprobación registrada:** 2026-10-18 (sesión previa, según el contexto confirmado por el usuario)
- **Contexto:** Un zone ID como `%eth0` identifica una zona/interfaz dependiente del contexto local y no forma parte de un valor global autónomo para esta calculadora.
- **Decisión:** Rechazar entradas IPv6 con zone ID usando `zone_id_not_supported`.
- **Motivo:** Evitar semántica dependiente del host y mantener el cálculo portable y puro.
- **Alternativas:** Aceptar y transportar el identificador, o quitarlo silenciosamente.
- **Consecuencias:** La validación del zone ID precede a la conversión genérica de dirección, para conservar el código de error específico.
- **Aprobación:** Aprobación previa informada por el usuario; no es una propuesta nueva de esta actualización.

## DEC-IPv6-04 — Aceptar direcciones IPv4 embebidas/mapeadas

- **Estado:** APROBADA (aprobada en sesión previa)
- **Fecha de aprobación registrada:** 2026-10-18 (sesión previa, según el contexto confirmado por el usuario)
- **Contexto:** La arquitectura IPv6 define representaciones que contienen una dirección IPv4, incluidas IPv4-mapped; existe además el formato IPv4-embedded para mecanismos de traducción.
- **Decisión:** Aceptar formas IPv6 válidas que incorporan una representación IPv4, y procesarlas como direcciones IPv6. No convertir la respuesta al contrato IPv4.
- **Motivo:** Aceptar las formas expresamente aprobadas sin ampliar el contrato a IPv4 independiente.
- **Alternativas:** Rechazar todas las formas con IPv4 textual o tratarlas como entrada IPv4.
- **Consecuencias:** Los ejemplos y pruebas deben cubrir al menos IPv4-mapped y un formato IPv4-embedded pertinente; la compatibilidad debe seguir las reglas de la forma IPv6 y sus prefijos, no una heurística textual.
- **Aprobación:** Aprobación previa informada por el usuario; no es una propuesta nueva de esta actualización. Referencias: RFC 4291 y RFC 6052.

## DEC-IPv6-05 — Clasificación basada en registros IANA curados

- **Estado:** APROBADA (aprobada en sesión previa)
- **Fecha de aprobación registrada:** 2026-10-18 (sesión previa, según el contexto confirmado por el usuario)
- **Contexto:** La clasificación IPv6 requiere un catálogo verificable y no debe inventar categorías o prefijos.
- **Decisión:** Clasificar con una tabla local curada a partir de los registros IANA IPv6 pertinentes, con nombre, prefijo, código estable y referencia/fecha de actualización.
- **Motivo:** Mantener resultados repetibles y disponibles sin conectividad, con procedencia auditable.
- **Alternativas:** Heurísticas basadas en rangos amplios, consultas IANA en tiempo real o un booleano simplificado público/privado.
- **Consecuencias:** La tabla se debe revisar ante cambios de los registros; las etiquetas describen asignaciones registrales y no garantizan enrutabilidad o alcanzabilidad. El vocabulario exacto y la precedencia de rangos se revisarán contra los registros al implementarla.
- **Aprobación:** Aprobación previa informada por el usuario; no es una propuesta nueva de esta actualización. Fuentes: registros IANA enlazados en `requisitos.md` y `api-contracts.md`.
- **URL de referencia:** https://www.iana.org/assignments/iana-ipv6-special-registry
- **Fecha de extracción:** PENDIENTE. La fecha de extracción se fija en el commit que implementa la tabla de clasificación; esta decisión no la fija hoy.

## DEC-IPv6-06 — Endpoint y router sin prefijo

- **Estado:** APROBADA
- **Fecha de aprobación:** 2026-10-18
- **Contexto:** Se requiere fijar el endpoint público y seguir la organización actual de la Calculadora IPv4/CIDR.
- **Decisión:** Usar `POST /api/v1/tools/ipv6/calculate`; el router no tendrá `prefix` y declarará la ruta completa.
- **Motivo:** Mantener simetría de ruta y evitar duplicar prefijos entre router y operación.
- **Alternativas:** Router con `prefix="/api/v1/tools/ipv6"` y ruta relativa `/calculate`.
- **Consecuencias:** El contrato y futuras pruebas HTTP usan exactamente el endpoint aprobado.
- **Aprobación:** Aprobación explícita del usuario en F5, 2026-10-18.

## DEC-IPv6-07 — Errores de dominio mediante el handler común

- **Estado:** APROBADA (confirmada al verificar `domain_error_handler` en `src/netops_desk/api/exceptions.py`)
- **Fecha de verificación:** 2026-10-18
- **Contexto:** F5 pidió verificar la traducción real de errores antes de formalizar el contrato IPv6.
- **Decisión:** El dominio utiliza `DomainError` con códigos `invalid_cidr`, `invalid_prefix` y `zone_id_not_supported`. El `domain_error_handler` existente devuelve HTTP 422 y `{ "error": exc.code, "detail": exc.message }`. La ruta no implementa una traducción propia.
- **Motivo:** Preservar la separación entre reglas de dominio y transporte HTTP y cumplir el contrato común de DEC-012.
- **Alternativas:** Lanzar HTTPException desde el dominio o mapear manualmente cada `DomainError` en la ruta; no se adoptan.
- **Consecuencias:** Errores de esquema siguen los handlers Pydantic comunes; errores HTTP 400/404/405/415 y excepciones 500 siguen el documento común del Módulo 1.
- **Evidencia:** `src/netops_desk/api/exceptions.py`, `domain_error_handler`, y `docs/modulo1/api-contracts.md`.
- **Aprobación:** Confirmación expresa del usuario en F5; la semántica HTTP deriva del handler vigente verificado estáticamente.

## DEC-IPv6-08 — `total_addresses` como cadena decimal

- **Estado:** APROBADA EN ESTE CONTRATO
- **Fecha:** 2026-10-18
- **Contexto:** El espacio IPv6 permite hasta `2^128` direcciones. Ese entero supera `Number.MAX_SAFE_INTEGER` y no puede representarse con exactitud como número JavaScript.
- **Decisión:** Serializar `total_addresses` como cadena decimal, por ejemplo `"18446744073709551616"` para `/64` y `"340282366920938463463374607431768211456"` para `/0`.
- **Motivo:** Preservar exactitud de extremo a extremo en JSON y frontend.
- **Alternativas:** Número JSON de doble precisión (descartado por pérdida de exactitud), valor hexadecimal o dos campos de palabra alta/baja.
- **Consecuencias:** El cliente conserva y muestra el valor textual; no lo parsea a `Number`. Es una divergencia deliberada respecto al contrato IPv4; no implica cambiar IPv4.
- **Aprobación:** Parte del alcance contractual explícito autorizado por el usuario en F5, 2026-10-18.
