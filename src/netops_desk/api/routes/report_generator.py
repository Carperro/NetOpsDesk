"""Rutas de la API para el Generador de Informes."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.report_generator import ReportGeneratorInput, ReportGeneratorOutput
from netops_desk.report_generator import generate_report

router = APIRouter(tags=["Report Generator"])
_report_semaphore = asyncio.Semaphore(5)

@router.post("/api/v1/tools/report-generator/generate", response_model=ReportGeneratorOutput)
async def generate_report_endpoint(
    body: ReportGeneratorInput,
    _: None = Depends(require_json_content_type),
) -> ReportGeneratorOutput:
    
    try:
        await asyncio.wait_for(_report_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Demasiadas solicitudes simultáneas."
        )

    try:
        # Pasamos el body como diccionario (model_dump) al dominio
        markdown = await run_in_threadpool(generate_report, data=body.model_dump())
        return ReportGeneratorOutput(report_markdown=markdown)
    finally:
        _report_semaphore.release()