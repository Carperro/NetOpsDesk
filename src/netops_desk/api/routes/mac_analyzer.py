"""Rutas de la API para el Analizador MAC."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.mac_analyzer import MacAnalyzerInput, MacAnalyzerOutput
from netops_desk.api.infrastructure.mac_runner import MacVendorLookupAdapter
from netops_desk.mac_analyzer import MacVendorLookupRunner, execute_mac_analyzer

router = APIRouter(tags=["MAC Analyzer"])
_mac_semaphore = asyncio.Semaphore(5)

def get_mac_runner() -> MacVendorLookupRunner:
    return MacVendorLookupAdapter()

@router.post("/api/v1/tools/mac-analyzer/execute", response_model=MacAnalyzerOutput)
async def execute_mac_analyzer_endpoint(
    body: MacAnalyzerInput,
    _: None = Depends(require_json_content_type),
    runner: MacVendorLookupRunner = Depends(get_mac_runner),
) -> MacAnalyzerOutput:
    
    try:
        await asyncio.wait_for(_mac_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Demasiadas solicitudes simultáneas."
        )

    try:
        result = await run_in_threadpool(execute_mac_analyzer, mac=body.mac, runner=runner)
        return MacAnalyzerOutput(**result)
    finally:
        _mac_semaphore.release()