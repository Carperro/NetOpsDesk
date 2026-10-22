"""Rutas de la API para el Analizador de Rutas."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.route_analyzer import RouteAnalyzerOutput
from netops_desk.api.infrastructure.route_runner import SubprocessRouteRunner
from netops_desk.route_analyzer import RouteRunner, execute_route_analyzer

router = APIRouter(tags=["Route Analyzer"])

_route_semaphore = asyncio.Semaphore(5)

def get_route_runner() -> RouteRunner:
    return SubprocessRouteRunner()


@router.get(
    "/api/v1/tools/route-analyzer/execute",
    response_model=RouteAnalyzerOutput,
    summary="Analiza el gateway y las rutas locales",
)
async def execute_route_analyzer_endpoint(
    runner: RouteRunner = Depends(get_route_runner),
) -> RouteAnalyzerOutput:
    
    try:
        await asyncio.wait_for(_route_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Hay demasiados análisis en ejecución. Esperá unos segundos."
        )

    try:
        # Al no haber body, no pasamos parámetros al dominio más que el runner
        result = await run_in_threadpool(
            execute_route_analyzer,
            runner=runner,
        )
        return RouteAnalyzerOutput(**result)
    finally:
        _route_semaphore.release()