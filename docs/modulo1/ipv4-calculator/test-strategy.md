# Estrategia y cobertura de pruebas - Calculadora IPv4/CIDR

## Estado

Los módulos `tests/test_ipv4_domain.py`, `tests/test_api_ipv4.py` y `tests/test_frontend_static.py` contienen pruebas automatizadas. Esta estrategia identifica cobertura presente leyendo sus casos y aserciones; no informa una ejecución ni un resultado de Pytest. Los resultados de cada ejecución deben indicar por separado recolectadas, aprobadas, fallidas, omitidas y advertencias.

## Dominio

`test_ipv4_domain.py` contiene casos para:

- Cálculo por CIDR y por dirección/máscara, red, broadcast, wildcard, cantidades y normalización de bits de host.
- `/0`, `/30`, `/31` y `/32` en los modos aplicables. Para `/31` y `/32` verifica cantidad total, capacidad, broadcast y límites utilizables en `conventional` y `point-to-point`.
- Fallback convencional y warning `point_to_point_not_applicable` para prefijos no aplicables.
- Estructura binaria de seis claves y nulabilidad coherente con los campos originales.
- Selección del prefijo inverso más largo que satisface la capacidad, ejemplos con 1, 2 y 3 hosts, y límite de capacidad `/0`.
- Códigos de error del dominio para IPv4/prefijos inválidos, tipos, modo, entrada incompleta, mezcla de formas, máscara no contigua y capacidad insuficiente.

El dominio no decide códigos HTTP ni procesa JSON.

## API y precedencia

`test_api_ipv4.py` contiene casos para respuestas directas e inversas, normalización/warnings, errores de tipos y valores, campos desconocidos, incompatibilidad, entrada faltante, JSON malformado, UTF-8 inválido, Content-Type, método, capacidad insuficiente y error inesperado. También incluye pruebas con varios defectos para estas precedencias:

| Frontera cubierta por el caso fuente | Expectativa comprobada |
|---|---|
| Método no permitido con JSON malformado | `405 method_not_allowed` |
| Content-Type no JSON con cuerpo malformado | `415 unsupported_media_type` |
| Campo desconocido junto con incompatibilidad | `422 unknown_field` |
| Incompatibilidad frente a campo requerido ausente | `422 incompatible_inputs` |
| Incompatibilidad frente a tipo inválido | `422 incompatible_inputs` |
| Campo requerido ausente frente a tipo inválido | `422 missing_field` |
| IPv4 inválida frente a máscara no contigua | `422 invalid_value` |
| Tipo incorrecto frente a máscara no contigua | `422 invalid_type` |

Otros casos del archivo comprueban Content-Type ausente (`415`), JSON válido cuyo valor superior no es objeto (`422 invalid_body`), múltiples campos desconocidos en orden alfabético, y ausencia de `mode` en cálculo inverso (`422 missing_field`).

El contrato implementado distingue JSON malformado (`422 invalid_json`) de errores HTTP 400 al leer/interpretar el cuerpo, incluidos bytes UTF-8 inválidos (`400 invalid_json`) según los casos fuente existentes. La documentación anterior excluía HTTP 400; se registra aquí la diferencia, sin convertirla en una decisión histórica aprobada.

`test_frontend_static.py` comprueba la entrega de HTML/CSS/JS, los formularios, los campos y modos, los mensajes/códigos contemplados por el JavaScript, el render de warnings y datos dinámicos, y una solicitud básica a la API. Son comprobaciones HTTP y estáticas; no simulan la ejecución del navegador ni una interacción real completa.

## Dependencias y ejecución

`pyproject.toml` declara Pytest y la distribución `httpx2` en el grupo opcional `test`; las pruebas construyen el cliente con `fastapi.testclient.TestClient`. DEC-006 conserva la decisión histórica que nombra HTTPX. El estado actual de `pyproject.toml` se documenta como implementación observada y no como evidencia de una aprobación formal de la sustitución.

Desde la raíz, con el entorno instalado: `python -m pytest`. Una prueba no ejecutada no cuenta como aprobada. No se ejecutaron pruebas como parte de esta actualización documental.

## Clasificación aplazada

La clasificación no se prueba ni se devuelve en la respuesta pública actual. El catálogo exacto requerido no se ha confirmado; no se debe documentar una lista parcial como completa.

## Criterio de aceptación

La cobertura presente puede revisarse directamente en los tres archivos de pruebas indicados. Para considerar una ejecución satisfactoria, deben ejecutarse las pruebas pertinentes y reportarse los resultados reales. La aceptación del módulo requiere verificar las reglas documentadas, incluidas las condiciones de límite, el contrato HTTP y la integración de la interfaz que se apruebe para esta etapa.
