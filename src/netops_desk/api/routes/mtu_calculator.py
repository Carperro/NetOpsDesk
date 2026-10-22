"""Rutas de la API para la Calculadora MTU."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.mtu_calculator import MtuInput, MtuOutput
from netops_desk.mtu_calculator import calculate_mtu

router = APIRouter(tags=["MTU Calculator"])
_mtu_semaphore = asyncio.Semaphore(5)

@router.post("/api/v1/tools/mtu-calculator/calculate", response_model=MtuOutput)
async def calculate_mtu_endpoint(
    body: MtuInput,
    _: None = Depends(require_json_content_type),
) -> MtuOutput:
    
    try:
        await asyncio.wait_for(_mtu_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Demasiadas solicitudes simultáneas."
        )

    try:
        # Es matemática pura, no necesita run_in_threadpool
        result = calculate_mtu(
            mtu=body.mtu,
            ip_version=body.ip_version,
            transport=body.transport,
            tunnel=body.tunnel
        )
        return MtuOutput(**result)
    finally:
        _mtu_semaphore.release()