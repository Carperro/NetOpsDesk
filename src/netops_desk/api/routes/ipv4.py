"""Rutas de la API para la calculadora IPv4/CIDR.

Este módulo expone la lógica de dominio (netops_desk.ipv4) a través de
FastAPI. Toda la validación estructural la realizan Pydantic y FastAPI,
excepto la verificación de Content-Type, que se hace en una dependencia
explícita para devolver 415 con un código contractual.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.models.ipv4 import (
    IPV4DirectOutput,
    IPV4Input,
    IPV4InverseOutput,
)
from netops_desk.ipv4 import calculate_direct, calculate_inverse


router = APIRouter(tags=["IPv4 Calculator"])


@router.post(
    "/api/v1/tools/ipv4/calculate",
    response_model=IPV4DirectOutput | IPV4InverseOutput,
    summary="Calcula información IPv4/CIDR",
    description=(
        "Acepta cálculo directo (cidr o address+netmask) o inverso "
        "(required_hosts+mode)."
    ),
)
async def calculate_ipv4(
    body: IPV4Input,
    _: None = Depends(require_json_content_type),
) -> IPV4DirectOutput | IPV4InverseOutput:
    """Ejecuta el cálculo solicitado y devuelve el resultado.

    La decisión entre cálculo directo e inverso se toma según los campos
    presentes: si 'required_hosts' está presente, es inverso; si no, directo.
    """
    if body.required_hosts is not None:
        result = calculate_inverse(
            required_hosts=body.required_hosts,
            mode=body.mode,
        )
        return IPV4InverseOutput(**result)

    result = calculate_direct(
        cidr=body.cidr,
        address=body.address,
        netmask=body.netmask,
        mode=body.mode,
    )
    return IPV4DirectOutput(**result)
