from pydantic import BaseModel, Field
from typing import List

class OverlapInput(BaseModel):
    networks: List[str] = Field(
        ..., 
        min_length=2, 
        description="Lista de redes a comparar (mínimo 2). Ej: ['192.168.1.0/24', '10.0.0.0/8']"
    )

class OverlapConflict(BaseModel):
    network_a: str
    network_b: str
    message: str

class OverlapOutput(BaseModel):
    networks: List[str]
    has_overlap: bool
    overlaps: List[OverlapConflict]