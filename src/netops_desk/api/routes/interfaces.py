"""Rutas de la API para Interfaces de Red."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.interfaces import InterfacesOutput
from netops_desk.api.infrastructure.interfaces_runner import PsutilInterfacesRunner
from netops_desk.interfaces import NetworkInterfacesRunner, execute_interfaces

router = APIRouter(tags=["Interfaces"])
_interfaces_semaphore = asyncio.Semaphore(5)

def get_interfaces_runner() -> NetworkInterfacesRunner:
    return PsutilInterfacesRunner()

@router.get("/api/v1/tools/interfaces/execute", response_model=InterfacesOutput)
async def execute_interfaces_endpoint(
    runner: NetworkInterfacesRunner = Depends(get_interfaces_runner),
) -> InterfacesOutput:
    
    try:
        await asyncio.wait_for(_interfaces_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(status_code=status.HTTP_429_TOO_MANY_REQUESTS, error_code="too_many_requests", detail="Demasiados análisis simultáneos.")

    try:
        result = await run_in_threadpool(execute_interfaces, runner=runner)
        return InterfacesOutput(**result)
    finally:
        _interfaces_semaphore.release()