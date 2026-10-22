"""Rutas de la API para la calculadora IPv6/CIDR.

La ruta no captura DomainError: el handler global lo traduce a HTTP 422
con el sobre común {error, detail} (DEC-012).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.models.ipv6 import IPv6Input, IPv6Output
from netops_desk.ipv6 import calculate


router = APIRouter(tags=["IPv6 Calculator"])


@router.post(
    "/api/v1/tools/ipv6/calculate",
    response_model=IPv6Output,
    summary="Calcula información IPv6/CIDR",
    description=(
        "Acepta un CIDR IPv6 y devuelve la red, la última dirección "
        "del bloque y el total de direcciones como string decimal."
    ),
)
async def calculate_ipv6(
    body: IPv6Input,
    _: None = Depends(require_json_content_type),
) -> IPv6Output:
    """Ejecuta el cálculo IPv6 y devuelve el resultado."""
    result = calculate(cidr=body.cidr)
    return IPv6Output(**result)