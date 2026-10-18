from fastapi import APIRouter, Depends
from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.models import VlsmInput, VlsmOutput
from netops_desk.vlsm import calculate_vlsm

router = APIRouter(prefix="/api/v1/tools/vlsm", tags=["VLSM"])

@router.post("/calculate", response_model=VlsmOutput)
async def calculate_vlsm_endpoint(
    payload: VlsmInput,
    _: None = Depends(require_json_content_type),
):
    # Convertimos los modelos de solicitud a los datos que espera el dominio.
    requirements_list = [
        {"name": req.name, "hosts": req.hosts}
        for req in payload.requirements
    ]
    return calculate_vlsm(payload.network_cidr, requirements_list)
