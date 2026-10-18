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
