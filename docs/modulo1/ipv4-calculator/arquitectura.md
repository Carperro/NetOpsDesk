# Arquitectura implementada - Calculadora IPv4/CIDR

## Componentes

### Dominio: `src/netops_desk/ipv4.py`

El módulo contiene `calculate_direct` y `calculate_inverse`, las reglas de capacidad y normalización, y los errores `DomainError`/`ErrorCode`. Los resultados se describen mediante `TypedDict` (`IPv4DirectResult`, `IPv4InverseResult`); las advertencias y la representación binaria también tienen tipos estructurados. El dominio usa `ipaddress` de la biblioteca estándar y no depende de FastAPI, Pydantic, HTTP ni del frontend. Los mensajes de dominio están en español.

### API

- `api/models.py` define el modelo de entrada único `IPV4Input`, con campos extra prohibidos (`extra="forbid"`), validación de formas y tipos, `PydanticCustomError` para errores contractuales y los modelos de salida directa e inversa.
- `api/routes/ipv4.py` expone `POST /api/v1/tools/ipv4/calculate`. La dependencia `require_json_content_type` valida el tipo MIME. La ruta recibe `IPV4Input` y elige `calculate_inverse` cuando `required_hosts` está presente; en otro caso invoca `calculate_direct`.
- `api/exceptions.py` centraliza `APIValidationError`, `api_validation_error_handler`, `pydantic_validation_error_handler`, `http_exception_handler`, `domain_error_handler` y `general_exception_handler`. Traduce errores al cuerpo uniforme `{ "error": string, "detail": string }`.
- `api/main.py` crea la aplicación, registra los handlers, incluye la ruta y sirve `static/` bajo `/static`, con `index.html` en `/`.

La API no añade servicios ni persistencia. La traducción de errores y sus códigos vigentes están descritos en `api-contracts.md`. El manejo HTTP incluye actualmente `400 invalid_json` para errores HTTP 400, además del `422 invalid_json` generado por errores de sintaxis Pydantic; esa diferencia refleja el código y las pruebas fuente, pero no la decisión previa que retiraba 400 del contrato.

### Interfaz

La interfaz consiste en HTML, CSS y JavaScript vanilla en `src/netops_desk/static/`. FastAPI entrega la página y los recursos desde el mismo origen. `app.js` envía solicitudes a la API y presenta resultados, warnings y errores; los cálculos permanecen en el dominio.

### Pruebas

`tests/test_ipv4_domain.py` comprueba cálculos y errores del dominio; `tests/test_api_ipv4.py` comprueba HTTP y validación; `tests/test_frontend_static.py` comprueba la entrega y estructura estática, además de compatibilidad básica de la API. Los archivos demuestran que estas pruebas están implementadas, no que se ejecutaron en una sesión determinada.

## Flujo de una solicitud

1. FastAPI enruta la solicitud al endpoint POST; una ruta/método no encontrado se procesa con el handler HTTP.
2. FastAPI valida el cuerpo contra `IPV4Input`; la dependencia de ruta comprueba `Content-Type` y rechaza valores distintos de `application/json` con `415 unsupported_media_type`.
3. El modelo rechaza campos extra, incompatibilidades, campos faltantes y tipos/valores inválidos. La traducción Pydantic prioriza los errores de campos desconocidos si coexisten con otros errores y ordena alfabéticamente los nombres agrupados.
4. La ruta deriva la operación de `required_hosts` y llama al dominio.
5. Los handlers convierten errores de dominio, API, validación, HTTP o inesperados en respuestas JSON uniformes.

La precedencia específica cubierta en los tests está enumerada en `test-strategy.md`. No debe inferirse un orden para combinaciones no cubiertas solo a partir de este resumen de capas.

## Dependencias y operación

Dependencias de ejecución declaradas en `pyproject.toml`: FastAPI, Pydantic y Uvicorn. Las dependencias opcionales de pruebas declaran la distribución `httpx2` y Pytest. Las herramientas de desarrollo declaradas son Ruff, Black y Mypy. Las pruebas usan `fastapi.testclient.TestClient`; no importan directamente el paquete `httpx2`.

Para servir localmente, Uvicorn debe enlazarse a `127.0.0.1`, de acuerdo con las restricciones del MVP. Comando de referencia: `python -m uvicorn netops_desk.api.main:app --host 127.0.0.1 --port 8000`.

La clasificación de direcciones continúa aplazada y no se incluye en las respuestas actuales. No se incorpora aquí una tabla de asignaciones IANA ni se infiere su catálogo.
