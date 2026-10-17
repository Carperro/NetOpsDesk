# Requisitos de Subnetting IPv4

## Alcance y estado

Subnetting IPv4 es la herramienta 2 del Módulo 1 y forma parte del MVP por la ampliación de alcance registrada en `docs/modulo1/ipv4-calculator/decision-log.md` (DEC-009).

Este documento distingue los criterios funcionales aprobados de los detalles que solo describen el código actual. No convierte las limitaciones observadas en requisitos.

## Modos de cálculo

La herramienta ofrece dos operaciones sobre una red base CIDR:

1. **Por cantidad de subredes:** recibe `network_cidr` y `subnet_count`, ambos obligatorios. `subnet_count` debe ser mayor que cero. El código calcula la cantidad de bits necesaria con `ceil(log2(subnet_count))`, divide la red base en bloques de igual prefijo y devuelve los primeros tantos bloques como se solicitaron. Si la red base no tiene capacidad para esa división, el cálculo falla.
2. **Por hosts requeridos:** recibe `network_cidr` y `required_hosts`, ambos obligatorios. `required_hosts` debe ser mayor que cero. El código calcula un prefijo de subred que busca satisfacer la cantidad requerida y devuelve las subredes resultantes dentro de la red base. La fórmula, sus límites actuales y la salida están descritos en `api-contracts.md`.

Los nombres de campos y las formas HTTP se detallan en `api-contracts.md`.

## Normalización

Si la dirección incluida en `network_cidr` tiene bits de host activos, se normaliza a la dirección de red. La respuesta indica el hecho con `was_normalized = true`.

**Comportamiento actual:** `original_network` contiene la red CIDR ya normalizada; no conserva literalmente el texto de entrada. El nombre del campo puede inducir a pensar que devuelve la entrada original.

## Prefijos `/31` y `/32`

La regla adoptada para enlaces IPv4 punto a punto `/31` sigue [RFC 3021](https://www.rfc-editor.org/rfc/rfc3021.html): las dos direcciones del bloque se interpretan como direcciones de host y no existe broadcast dirigido dedicado en ese enlace. El código calcula una capacidad de dos hosts para `/31`; su helper de capacidad calcula una para `/32`.

**Comportamiento observado que aún requiere reconciliación contractual:**

- El serializador toma `broadcast` de `ipaddress.IPv4Network.broadcast_address` y lo devuelve como cadena incluso para `/31` y `/32`.
- `first_host` y `last_host` se devuelven como `null` cuando el bloque tiene dos direcciones o menos; por eso la respuesta actual no expone las dos direcciones utilizables de un `/31` ni la dirección única de un `/32` en esos campos.
- El cálculo por hosts trata una solicitud de un host como un caso especial que selecciona `/31`. Sin embargo, una base `/31` solicitando dos hosts y una base `/32` solicitando un host pueden rechazarse porque el prefijo calculado resulta menor que el prefijo base. Esto no coincide con los valores que declara el helper de capacidad.

Estos puntos son una discrepancia de implementación y no deben interpretarse como una decisión funcional aprobada para la respuesta pública. La semántica exacta de los campos de rango y broadcast para estos límites requiere reconciliación antes de considerar cerrado el contrato.

## Límite de familia de direcciones

La herramienta se presenta como IPv4 y la interfaz valida una entrada IPv4/CIDR. El código de dominio llama a `ipaddress.ip_network` sin una comprobación explícita de `IPv4Network`; por lo tanto, la aceptación o rechazo de IPv6 por la API no está definida como requisito y queda pendiente de una especificación inequívoca.

## Verificación existente

`tests/test_subnetting.py` contiene pruebas del dominio para las dos operaciones, normalización, capacidad insuficiente y algunos casos límite. No existe una suite HTTP dedicada a los endpoints de Subnetting ni cobertura estática específica de esta herramienta en `tests/test_frontend_static.py`.
