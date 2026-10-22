"""Rutas de la API para la herramienta Traceroute."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.traceroute import TracerouteInput, TracerouteOutput
from netops_desk.api.infrastructure.traceroute_runner import SubprocessTracerouteRunner
from netops_desk.traceroute import TracerouteRunner, execute_traceroute

router = APIRouter(tags=["Traceroute"])

# Semáforo global (el servidor corre con 1 solo worker). Máximo 3 tracert a la vez.
_traceroute_semaphore = asyncio.Semaphore(3)

def get_traceroute_runner() -> TracerouteRunner:
    """Dependencia para inyectar el runner."""
    return SubprocessTracerouteRunner()


@router.post(
    "/api/v1/tools/traceroute/execute",
    response_model=TracerouteOutput,
    summary="Ejecuta un traceroute ICMP",
)
async def execute_traceroute_endpoint(
    body: TracerouteInput,
    _: None = Depends(require_json_content_type),
    runner: TracerouteRunner = Depends(get_traceroute_runner),
) -> TracerouteOutput:
    
    # Intentar adquirir el semáforo
    try:
        await asyncio.wait_for(_traceroute_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Hay demasiados traceroutes en ejecución. Esperá unos segundos."
        )

    try:
        result = await run_in_threadpool(
            execute_traceroute,
            host=body.host,
            max_hops=body.max_hops,
            runner=runner,
        )
        return TracerouteOutput(**result)
    finally:
        _traceroute_semaphore.release()