"""Rutas de la API para el Visor ARP."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.arp_viewer import ArpOutput
from netops_desk.api.infrastructure.arp_runner import SubprocessArpRunner
from netops_desk.arp_viewer import ArpRunner, execute_arp_viewer

router = APIRouter(tags=["ARP Viewer"])
_arp_semaphore = asyncio.Semaphore(5)

def get_arp_runner() -> ArpRunner:
    return SubprocessArpRunner()

@router.get("/api/v1/tools/arp-viewer/execute", response_model=ArpOutput)
async def execute_arp_endpoint(
    runner: ArpRunner = Depends(get_arp_runner),
) -> ArpOutput:
    
    try:
        await asyncio.wait_for(_arp_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Demasiadas consultas simultáneas. Esperá un momento."
        )

    try:
        result = await run_in_threadpool(execute_arp_viewer, runner=runner)
        return ArpOutput(**result)
    finally:
        _arp_semaphore.release()