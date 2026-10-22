"""Dependencias compartidas para validar solicitudes de la API."""

from __future__ import annotations

from fastapi import Request, status

from netops_desk.api.exceptions import APIValidationError


async def require_json_content_type(request: Request) -> None:
    """Rechaza solicitudes cuyo Content-Type no sea application/json."""
    content_type = request.headers.get("content-type", "")
    mime = content_type.split(";")[0].strip().lower()

    if mime != "application/json":
        raise APIValidationError(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error_code="unsupported_media_type",
            detail=(
                f"Content-Type '{content_type}' no soportado. "
                "Se espera 'application/json'."
            ),
        )

from fastapi import Header, HTTPException, status
from netops_desk.auth import decode_token
from netops_desk.exceptions import DomainError

async def get_current_user(authorization: str = Header(None)) -> dict:
    """Dependencia que valida el token JWT en cada request."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "detail": "Falta el token de autenticación."}
        )
    
    token = authorization.split(" ")[1]
    try:
        payload = decode_token(token)
        return payload
    except DomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": exc.code, "detail": exc.message}
        )