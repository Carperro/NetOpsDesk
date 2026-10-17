"""Punto de entrada de la aplicación FastAPI de NetOps Desk.

Crea la aplicación, registra los handlers de excepciones y monta los
routers y los archivos estáticos.

Los handlers de excepciones viven en netops_desk.api.exceptions: este
módulo solo se encarga de registrarlos en el orden correcto.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from netops_desk.api.exceptions import (
    APIValidationError,
    api_validation_error_handler,
    domain_error_handler,
    general_exception_handler,
    http_exception_handler,
    pydantic_validation_error_handler,
)
from netops_desk.api.routes.ipv4 import router as ipv4_router
from netops_desk.ipv4 import DomainError


# Directorio donde viven los archivos estáticos (HTML, CSS, JS).
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI.

    Usa el patrón factory para poder instanciar la app en tests con
    distinta configuración si hiciera falta.
    """
    app = FastAPI(
        title="NetOps Desk API",
        description="Herramientas de red para soporte IT.",
        version="0.1.0",
    )

    # Registramos los handlers de excepciones.
    # El orden importa: los más específicos primero, los generales al final.
    # FastAPI evalúa el tipo de excepción para elegir el handler adecuado.
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(APIValidationError, api_validation_error_handler)
    app.add_exception_handler(RequestValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Routers de la API.
    app.include_router(ipv4_router)

    # Archivos estáticos. Se monta DESPUÉS del router para no interceptar
    # las rutas /api/*; el prefijo /static es explícito para que no colisione
    # con la ruta raíz.
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def root() -> FileResponse:
        """Sirve el index.html de la aplicación en la ruta raíz."""
        return FileResponse(STATIC_DIR / "index.html")

    return app


# Instancia que Uvicorn importa: 'netops_desk.api.main:app'.
app = create_app()