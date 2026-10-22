"""Rutas de la API para la herramienta Ping."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.ping import PingInput, PingOutput
from netops_desk.api.infrastructure.ping_runner import SubprocessPingRunner
from netops_desk.ping import PingRunner, execute_ping

router = APIRouter(tags=["Ping"])

# Semáforo global (el servidor corre con 1 solo worker)
_ping_semaphore = asyncio.Semaphore(5)

def get_ping_runner() -> PingRunner:
    """Dependencia para inyectar el runner (fácilmente sobreescribible en tests)."""
    return SubprocessPingRunner()


@router.post(
    "/api/v1/tools/ping/execute",
    response_model=PingOutput,
    summary="Ejecuta un ping ICMP",
)
async def execute_ping_endpoint(
    body: PingInput,
    _: None = Depends(require_json_content_type),
    runner: PingRunner = Depends(get_ping_runner),
) -> PingOutput:
    
    # Intentar adquirir el semáforo sin bloquear indefinidamente
    try:
        # 0.01s es suficiente para saber si está libre o no
        await asyncio.wait_for(_ping_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Hay demasiados pings en ejecución. Esperá unos segundos e intentá de nuevo."
        )

    try:
        # Ejecutamos el dominio en un hilo aparte para no bloquear FastAPI
        result = await run_in_threadpool(
            execute_ping,
            host=body.host,
            count=body.count,
            runner=runner,
        )
        return PingOutput(**result)
    finally:
        # Siempre liberar el semáforo, incluso si hubo error
        _ping_semaphore.release()