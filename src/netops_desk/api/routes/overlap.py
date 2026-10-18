from fastapi import APIRouter, HTTPException
from netops_desk.api.models import OverlapInput, OverlapOutput
from netops_desk.overlap import detect_overlaps
from netops_desk.exceptions import DomainError

router = APIRouter(prefix="/api/v1/tools/overlap", tags=["Overlap Detector"])

@router.post("/calculate", response_model=OverlapOutput)
async def calculate_overlap_endpoint(payload: OverlapInput):
    try:
        result = detect_overlaps(payload.networks)
        return result
    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.message)