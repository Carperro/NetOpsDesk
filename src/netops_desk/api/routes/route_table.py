"""Rutas de la API para la Tabla de Rutas."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.route_table import RouteTableOutput
from netops_desk.api.infrastructure.route_table_runner import SubprocessRouteTableRunner
from netops_desk.route_table import RouteTableRunner, execute_route_table

router = APIRouter(tags=["Route Table"])
_rt_semaphore = asyncio.Semaphore(5)

def get_route_table_runner() -> RouteTableRunner:
    return SubprocessRouteTableRunner()

@router.get("/api/v1/tools/route-table/execute", response_model=RouteTableOutput)
async def execute_route_table_endpoint(
    runner: RouteTableRunner = Depends(get_route_table_runner),
) -> RouteTableOutput:
    
    try:
        await asyncio.wait_for(_rt_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Demasiadas consultas simultáneas."
        )

    try:
        result = await run_in_threadpool(execute_route_table, runner=runner)
        return RouteTableOutput(**result)
    finally:
        _rt_semaphore.release()