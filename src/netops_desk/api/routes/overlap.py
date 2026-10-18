from fastapi import APIRouter, Depends
from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.models import OverlapInput, OverlapOutput
from netops_desk.overlap import detect_overlaps

router = APIRouter(prefix="/api/v1/tools/overlap", tags=["Overlap Detector"])

@router.post("/calculate", response_model=OverlapOutput)
async def calculate_overlap_endpoint(
    payload: OverlapInput,
    _: None = Depends(require_json_content_type),
):
    return detect_overlaps(payload.networks)
