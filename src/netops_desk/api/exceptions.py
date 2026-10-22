"""Handlers de excepciones para la API de NetOps Desk.

Centraliza la traducción de excepciones (de dominio, de validación Pydantic
y HTTP genéricas) a respuestas JSON uniformes con códigos de error estables
del contrato.

Formato de respuesta de error:
    {"error": "<código contractual>", "detail": "<mensaje legible>"}
"""

from __future__ import annotations

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from netops_desk.exceptions import DomainError


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Respuesta uniforme de error
# ---------------------------------------------------------------------------

def _error_response(status_code: int, error_code: str, detail: str) -> JSONResponse:
    """Construye una respuesta JSON uniforme de error."""
    return JSONResponse(
        status_code=status_code,
        content={"error": error_code, "detail": detail},
    )


# ---------------------------------------------------------------------------
# Excepción de la capa API
# ---------------------------------------------------------------------------

class APIValidationError(Exception):
    """Error de validación originado en la capa de API.

    A diferencia de DomainError (que pertenece al dominio puro y no sabe
    de HTTP), este error conoce el código de estado que debe devolverse.
    """

    def __init__(self, status_code: int, error_code: str, detail: str) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        super().__init__(detail)


# ---------------------------------------------------------------------------
# Mapeo de errores de Pydantic a códigos contractuales
# ---------------------------------------------------------------------------

# Códigos de error de Pydantic v2 → códigos del contrato de la API.
_PYDANTIC_ERROR_MAP: dict[str, str] = {
    "extra_forbidden": "unknown_field",
    "missing": "missing_field",
    "incompatible_inputs": "incompatible_inputs",   # ← nuevo
    "missing_field": "missing_field",                # ← nuevo
    "string_type": "invalid_type",
    "int_type": "invalid_type",
    "int_parsing": "invalid_type",
    "float_parsing": "invalid_type",
    "bool_type": "invalid_type",
    "list_type": "invalid_type",
    "dict_type": "invalid_type",
    "invalid_type": "invalid_type",
    "invalid_value": "invalid_value",
    "literal_error": "invalid_value",
    "enum": "invalid_value",
    "value_error": "invalid_value",
    "greater_than": "invalid_value",
    "greater_than_equal": "invalid_value",
    "less_than": "invalid_value",
    "less_than_equal": "invalid_value",
    "string_too_short": "invalid_value",
    "string_too_long": "invalid_value",
    "too_short": "invalid_value",
    "too_long": "invalid_value",
    "string_pattern_mismatch": "invalid_value",
    "ip_v4_address": "invalid_value",
    "ip_v4_network": "invalid_value",
    "ip_any_address": "invalid_value",
    "json_invalid": "invalid_json",
    "model_attributes_type": "invalid_body",
    "model_type": "invalid_body",
}

# Códigos HTTP → códigos contractuales.
_HTTP_STATUS_MAP: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_405_METHOD_NOT_ALLOWED: "method_not_allowed",
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "unsupported_media_type",
}


def _format_pydantic_error(err: dict) -> tuple[str, str]:
    """Traduce un error individual de Pydantic a (código, mensaje)."""
    err_type = err.get("type", "")
    loc = err.get("loc", [])
    error_code = _PYDANTIC_ERROR_MAP.get(err_type, "invalid_value")

    # Construimos la ruta del campo, filtrando elementos internos de Pydantic.
    # Pydantic puede insertar marcadores como 'body' o 'function-after[...]'
    # en el 'loc' cuando hay validadores encadenados. Al usuario solo le
    # interesa el nombre real del campo, que es el último elemento.

    partes_utiles = [
        str(part)
        for part in loc
        if part != "body" and not str(part).startswith("function-")
    ]

    field_path = partes_utiles[-1] if partes_utiles else ""

    # Mensajes en español para los casos más comunes del contrato.
    if err_type == "extra_forbidden":
        detail = f"Campo desconocido: '{field_path}'."
    elif err_type == "missing":
        detail = f"Falta el campo requerido: '{field_path}'."
    elif err_type == "string_type":
        detail = f"El campo '{field_path}' debe ser una cadena."
    elif err_type == "int_type":
        detail = f"El campo '{field_path}' debe ser un número entero."
    elif err_type == "ip_v4_address":
        detail = f"El campo '{field_path}' debe ser una dirección IPv4 válida."
    elif err_type == "literal_error":
        detail = f"El campo '{field_path}' tiene un valor no permitido."
    elif err_type == "greater_than":
        detail = f"El campo '{field_path}' debe ser mayor que el mínimo permitido."
    elif err_type == "json_invalid":
        detail = "El cuerpo de la petición no es JSON válido."
    elif err_type in {"incompatible_inputs", "missing_field", "invalid_type", "invalid_value"}:
        detail = err.get("msg") or "La solicitud contiene un dato no válido."
    elif err_type in {"int_parsing", "float_parsing"}:
        detail = f"El campo '{field_path}' debe contener un número válido."
    elif err_type in {"string_too_short", "too_short"}:
        detail = f"El campo '{field_path}' no alcanza la longitud o cantidad mínima requerida."
    elif err_type in {"string_too_long", "too_long"}:
        detail = f"El campo '{field_path}' supera la longitud o cantidad máxima permitida."
    elif err_type == "string_pattern_mismatch":
        detail = f"El campo '{field_path}' no tiene el formato requerido."
    elif err_type in {"greater_than", "greater_than_equal", "less_than", "less_than_equal"}:
        detail = f"El valor del campo '{field_path}' está fuera del límite permitido."
    else:
        detail = (
            f"El campo '{field_path}' tiene un tipo, formato o valor no válido."
            if field_path
            else "La solicitud contiene un tipo, formato o valor no válido."
        )

    return error_code, detail


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Traduce un DomainError a una respuesta HTTP 422 uniforme."""
    logger.warning(
        "DomainError en %s: %s - %s", request.url.path, exc.code, exc.message
    )
    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error_code=exc.code,
        detail=exc.message,
    )


async def api_validation_error_handler(
    request: Request, exc: APIValidationError
) -> JSONResponse:
    """Traduce un APIValidationError a una respuesta HTTP uniforme."""
    logger.warning(
        "APIValidationError en %s: %s - %s",
        request.url.path,
        exc.error_code,
        exc.detail,
    )
    return _error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        detail=exc.detail,
    )

async def pydantic_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Traduce un RequestValidationError de FastAPI/Pydantic.

    Toma el primer error y lo mapea a un código contractual. Si hay
    varios campos desconocidos, los agrupa en un solo mensaje ordenado.
    """
    errors = exc.errors()
    if not errors:
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            error_code="validation_error",
            detail="Error de validación en la petición.",
        )

    # Caso especial: varios campos desconocidos juntos.
    extra_errors = [e for e in errors if e.get("type") == "extra_forbidden"]
    if extra_errors:
        campos = sorted(
            str(e["loc"][-1]) for e in extra_errors if e.get("loc")
        )
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            error_code="unknown_field",
            detail=f"Campos desconocidos: {', '.join(campos)}.",
        )

    error_code, detail = _format_pydantic_error(errors[0])

    logger.info(
        "ValidationError en %s: %s - %s", request.url.path, error_code, detail
    )

    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error_code=error_code,
        detail=detail,
    )

async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Traduce HTTPException (400, 404, 405, etc.) a respuesta JSON uniforme."""
    status_code = exc.status_code
    error_code = _HTTP_STATUS_MAP.get(status_code, f"http_{status_code}")

    if status_code == status.HTTP_401_UNAUTHORIZED:
        if isinstance(exc.detail, dict):
            return JSONResponse(status_code=status_code, content=exc.detail)
        return _error_response(
            status_code=status_code,
            error_code="unauthorized",
            detail=str(exc.detail or "La autenticación es requerida."),
        )

    # Mensajes en español para los errores que produce FastAPI/Starlette.
    if status_code == status.HTTP_404_NOT_FOUND:
        detail = "Recurso no encontrado."
    elif status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        detail = "El método de solicitud no está permitido para esta ruta."
    elif status_code == status.HTTP_400_BAD_REQUEST and str(exc.detail) == "There was an error parsing the body":
        error_code = "invalid_json"
        detail = "El cuerpo de la petición no es JSON válido."
    else:
        detail = "La solicitud no pudo completarse por un error HTTP."

    logger.info(
        "HTTPException %d en %s: %s", status_code, request.url.path, detail
    )

    return _error_response(
        status_code=status_code,
        error_code=error_code,
        detail=detail,
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Captura cualquier excepción no controlada y devuelve un 500 uniforme."""
    logger.exception("Excepción no controlada en %s", request.url.path)
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="internal_error",
        detail="Error interno del servidor.",
    )
