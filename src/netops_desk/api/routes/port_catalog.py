"""Rutas de la API para el Catálogo de Puertos."""

import asyncio
from fastapi import APIRouter, Depends, Query, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.port_catalog import PortCatalogOutput
from netops_desk.port_catalog import search_ports

router = APIRouter(tags=["Port Catalog"])
_port_semaphore = asyncio.Semaphore(5)

@router.get("/api/v1/tools/port-catalog/search", response_model=PortCatalogOutput)
async def search_ports_endpoint(
    query: str = Query(default="", description="Buscar por puerto o servicio")
) -> PortCatalogOutput:
    
    try:
        await asyncio.wait_for(_port_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Demasiadas consultas simultáneas."
        )

    try:
        # Es una búsqueda en memoria súper rápida, no necesita threadpool.
        result = search_ports(query)
        return PortCatalogOutput(ports=result)
    finally:
        _port_semaphore.release()