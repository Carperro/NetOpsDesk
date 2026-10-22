"""Rutas de la API para el Asistente de Resolución."""

import asyncio
from fastapi import APIRouter, Depends, status
from netops_desk.api.exceptions import APIValidationError
from netops_desk.api.models.troubleshooter import SymptomOutput
from netops_desk.troubleshooter import get_symptom

router = APIRouter(tags=["Troubleshooter"])
_sym_semaphore = asyncio.Semaphore(5)

@router.get("/api/v1/tools/troubleshooter/symptoms/{symptom_id}", response_model=SymptomOutput)
async def get_symptom_endpoint(symptom_id: str) -> SymptomOutput:
    
    try:
        await asyncio.wait_for(_sym_semaphore.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        raise APIValidationError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="too_many_requests",
            detail="Demasiadas solicitudes simultáneas."
        )

    try:
        # Es una búsqueda en diccionario, no requiere threadpool
        result = get_symptom(symptom_id=symptom_id)
        return SymptomOutput(**result)
    finally:
        _sym_semaphore.release()