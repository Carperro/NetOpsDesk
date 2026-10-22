"""Rutas de la API para el Comparador de Configuraciones."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.config_comparator import ConfigComparatorInput, ConfigComparatorOutput
from netops_desk.config_comparator import compare_configs

router = APIRouter(tags=["Config Comparator"])
_diff_semaphore = asyncio.Semaphore(5)

@router.post("/api/v1/tools/config-comparator/compare", response_model=ConfigComparatorOutput)
async def compare_configs_endpoint(
    body: ConfigComparatorInput,
    _: None = Depends(require_json_content_type),
) -> ConfigComparatorOutput:
    
    try:
        await asyncio.wait_for(_diff_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Demasiadas solicitudes simultáneas."
        )

    try:
        # Usamos threadpool porque difflib puede tardar un poco con textos gigantes
        result = await run_in_threadpool(
            compare_configs, 
            config_a=body.config_a, 
            config_b=body.config_b
        )
        return ConfigComparatorOutput(**result)
    finally:
        _diff_semaphore.release()