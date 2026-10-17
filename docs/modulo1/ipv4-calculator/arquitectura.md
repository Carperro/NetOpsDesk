# Arquitectura implementada - Calculadora IPv4/CIDR

## Componentes

### Dominio: `src/netops_desk/ipv4.py`

El módulo contiene `calculate_direct` y `calculate_inverse`, las reglas de capacidad y normalización, y los errores `DomainError`/`ErrorCode`. Los resultados se describen mediante `TypedDict` (`IPv4DirectResult`, `IPv4InverseResult`); las advertencias y la representación binaria también tienen tipos estructurados (`DomainWarning`, `BinaryRepresentation`). El dominio usa `ipaddress` de la biblioteca estándar y no depende de FastAPI, Pydantic, HTTP ni del frontend. Los mensajes de dominio están en español.

### API

- `api/models/ipv4.py` define el modelo de entrada `IPV4Input`, con campos extra prohibidos (`extra="forbid"`), validación de formas y tipos, `PydanticCustomError` para errores contractuales y los modelos de salida directa (`IPV4DirectOutput`) e inversa (`IPV4InverseOutput`). `api/models/__init__.py` reexporta los modelos del paquete.
- `api/routes/ipv4.py` expone `POST /api/v1/tools/ipv4/calculate`. La dependencia `require_json_content_type` valida el tipo MIME. La ruta recibe `IPV4Input` y elige `calculate_inverse` cuando `required_hosts` está presente; en otro caso invoca `calculate_direct`.
- La herramienta Subnetting está separada en `src/netops_desk/subnetting.py`, `api/routes/subnetting.py` y `api/models/subnetting.py`; su contrato se documenta en `docs/modulo1/subnetting/`.
- `api/exceptions.py` centraliza `APIValidationError`, `api_validation_error_handler`, `pydantic_validation_error_handler`, `http_exception_handler`, `domain_error_handler` y `general_exception_handler`. Traduce errores al cuerpo uniforme `{ "error": string, "detail": string }`.
- `api/main.py` crea la aplicación, registra los handlers, incluye las rutas IPv4 y Subnetting, y sirve `static/` bajo `/static`, con páginas para ambas herramientas.

La API no añade servicios ni persistencia. La traducción de errores y sus códigos vigentes están descritos en `api-contracts.md`. El manejo HTTP incluye HTTP 400 `invalid_json` para errores de lectura o decodificación del cuerpo, además del HTTP 422 `invalid_json` generado por errores de sintaxis Pydantic. Esa distinción está formalizada en `decision-log.md` (DEC-007).

### Interfaz

La interfaz consiste en HTML, CSS y JavaScript vanilla en `src/netops_desk/static/`. FastAPI entrega las páginas y recursos desde el mismo origen. `ipv4.js` y `subnetting.js` envían solicitudes y muestran resultados, advertencias y errores; `sidebar.js` inyecta el menú lateral y `common.js` contiene comportamiento compartido. Los cálculos permanecen en los módulos de dominio.

### Pruebas

`tests/test_ipv4_domain.py` comprueba el dominio IPv4; `tests/test_api_ipv4.py` comprueba HTTP y validación de esa herramienta; `tests/test_subnetting.py` comprueba cálculos de Subnetting en el dominio; `tests/test_frontend_static.py` comprueba principalmente entrega y estructura de la interfaz IPv4; `tests/test_package_import.py` verifica que el paquete se pueda importar. No existe actualmente una suite HTTP dedicada a Subnetting.

## Flujo de una solicitud

1. FastAPI enruta la solicitud al endpoint POST; una ruta o método no encontrado se procesa con el handler HTTP.
2. FastAPI valida el cuerpo contra `IPV4Input`; la dependencia de ruta comprueba `Content-Type` y rechaza valores distintos de `application/json` con `415 unsupported_media_type`.
3. El modelo rechaza campos extra, incompatibilidades, campos faltantes y tipos/valores inválidos. La traducción Pydantic prioriza los errores de campos desconocidos si coexisten con otros errores y ordena alfabéticamente los nombres agrupados.
4. La ruta deriva la operación de `required_hosts` y llama al dominio.
5. Los handlers convierten errores de dominio, API, validación, HTTP o inesperados en respuestas JSON uniformes.

La precedencia específica cubierta en los tests está enumerada en `test-strategy.md`. No debe inferirse un orden para combinaciones no cubiertas solo a partir de este resumen de capas.

## Dependencias y operación

Dependencias de ejecución declaradas en `pyproject.toml`: FastAPI, Pydantic y Uvicorn. Las dependencias opcionales de pruebas declaran `httpx2` y Pytest; `httpx2` se mantiene intencionalmente por compatibilidad con Python 3.12. Las herramientas de desarrollo declaradas son Ruff, Black y Mypy. Las pruebas usan `fastapi.testclient.TestClient`; no importan directamente el paquete `httpx2`. El detalle está en `decision-log.md` (DEC-008).

Para servir localmente, Uvicorn debe enlazarse a `127.0.0.1`, de acuerdo con las restricciones del MVP. Comando de referencia:

```powershell
python -m uvicorn netops_desk.api.main:app --host 127.0.0.1 --port 8000
