"""Rutas de la API para el Generador de Comandos."""

import asyncio
from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.command_generator import CommandGeneratorInput, CommandGeneratorOutput
from netops_desk.command_generator import generate_command

router = APIRouter(tags=["Command Generator"])
_cmd_semaphore = asyncio.Semaphore(5)

@router.post("/api/v1/tools/command-generator/generate", response_model=CommandGeneratorOutput)
async def generate_command_endpoint(
    body: CommandGeneratorInput,
    _: None = Depends(require_json_content_type),
) -> CommandGeneratorOutput:
    
    try:
        await asyncio.wait_for(_cmd_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Demasiadas solicitudes simultáneas."
        )

    try:
        # Es procesamiento de strings rápido, no necesita threadpool
        result = generate_command(
            command_type=body.command_type,
            target=body.target,
            options=body.options
        )
        return CommandGeneratorOutput(**result)
    finally:
        _cmd_semaphore.release()