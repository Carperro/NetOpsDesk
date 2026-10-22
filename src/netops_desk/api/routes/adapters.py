"""Rutas de la API para Estado de Adaptadores."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.adapters import AdaptersOutput
from netops_desk.api.infrastructure.adapters_runner import PsutilAdaptersRunner
from netops_desk.adapters import AdaptersRunner, execute_adapters

router = APIRouter(tags=["Adapters"])
_adapters_semaphore = asyncio.Semaphore(5)

def get_adapters_runner() -> AdaptersRunner:
    return PsutilAdaptersRunner()

@router.get("/api/v1/tools/adapters/execute", response_model=AdaptersOutput)
async def execute_adapters_endpoint(
    runner: AdaptersRunner = Depends(get_adapters_runner),
) -> AdaptersOutput:
    
    try:
        await asyncio.wait_for(_adapters_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Demasiadas consultas simultáneas."
        )

    try:
        result = await run_in_threadpool(execute_adapters, runner=runner)
        return AdaptersOutput(**result)
    finally:
        _adapters_semaphore.release()