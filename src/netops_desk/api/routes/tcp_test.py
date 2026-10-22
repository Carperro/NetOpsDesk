"""Rutas de la API para la Prueba de puertos TCP."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.tcp_test import TcpTestInput, TcpTestOutput
from netops_desk.api.infrastructure.tcp_runner import SocketTcpRunner
from netops_desk.tcp_test import TcpRunner, execute_tcp_test

router = APIRouter(tags=["TCP Test"])

# Semáforo global (el servidor corre con 1 solo worker). Máximo 10 sockets a la vez.
_tcp_semaphore = asyncio.Semaphore(10)

def get_tcp_runner() -> TcpRunner:
    """Dependencia para inyectar el runner."""
    return SocketTcpRunner()


@router.post(
    "/api/v1/tools/tcp-test/execute",
    response_model=TcpTestOutput,
    summary="Prueba la conectividad a un puerto TCP",
)
async def execute_tcp_test_endpoint(
    body: TcpTestInput,
    _: None = Depends(require_json_content_type),
    runner: TcpRunner = Depends(get_tcp_runner),
) -> TcpTestOutput:
    
    try:
        await asyncio.wait_for(_tcp_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Hay demasiadas pruebas en ejecución. Esperá unos segundos."
        )

    try:
        result = await run_in_threadpool(
            execute_tcp_test,
            host=body.host,
            port=body.port,
            timeout_ms=body.timeout_ms,
            runner=runner,
        )
        return TcpTestOutput(**result)
    finally:
        _tcp_semaphore.release()