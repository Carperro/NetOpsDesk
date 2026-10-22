"""Rutas de la API para Diagnóstico DNS."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.dns_test import DnsTestInput, DnsTestOutput
from netops_desk.api.infrastructure.dns_runner import DnspythonRunner
from netops_desk.dns_test import DnsRunner, execute_dns_test

router = APIRouter(tags=["DNS Test"])

_dns_semaphore = asyncio.Semaphore(10)

def get_dns_runner() -> DnsRunner:
    return DnspythonRunner()


@router.post(
    "/api/v1/tools/dns-test/execute",
    response_model=DnsTestOutput,
    summary="Consulta registros DNS",
)
async def execute_dns_test_endpoint(
    body: DnsTestInput,
    _: None = Depends(require_json_content_type),
    runner: DnsRunner = Depends(get_dns_runner),
) -> DnsTestOutput:
    
    try:
        await asyncio.wait_for(_dns_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Hay demasiadas consultas en ejecución. Esperá unos segundos."
        )

    try:
        result = await run_in_threadpool(
            execute_dns_test,
            domain=body.domain,
            record_type=body.record_type,
            resolver=body.resolver,
            runner=runner,
        )
        return DnsTestOutput(**result)
    finally:
        _dns_semaphore.release()