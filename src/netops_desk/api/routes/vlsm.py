from fastapi import APIRouter, HTTPException
from netops_desk.api.models import VlsmInput, VlsmOutput
from netops_desk.vlsm import calculate_vlsm
from netops_desk.exceptions import DomainError

router = APIRouter(prefix="/api/v1/tools/vlsm", tags=["VLSM"])

@router.post("/calculate", response_model=VlsmOutput)
async def calculate_vlsm_endpoint(payload: VlsmInput):
    try:
        # Convertimos la lista de modelos Pydantic a una lista de diccionarios
        # que es lo que espera nuestra función de dominio
        requirements_list = [
            {"name": req.name, "hosts": req.hosts} 
            for req in payload.requirements
        ]
        
        result = calculate_vlsm(payload.network_cidr, requirements_list)
        return result

    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.message)