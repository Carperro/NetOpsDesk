from pydantic import BaseModel, ConfigDict, Field
from typing import List

class VlsmRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Nombre del departamento o área", min_length=1)
    hosts: int = Field(..., gt=0, description="Cantidad de hosts requeridos")

class VlsmInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    network_cidr: str = Field(..., description="Red base, ej: 192.168.1.0/24")
    requirements: List[VlsmRequirement] = Field(..., min_length=1, description="Lista de requerimientos")

class VlsmAllocated(BaseModel):
    name: str
    network: str
    prefix: int
    netmask: str
    broadcast: str
    first_host: str
    last_host: str
    total_ips: int
    hosts_needed: int

class VlsmRemaining(BaseModel):
    network: str
    broadcast: str
    total_ips: int

class VlsmOutput(BaseModel):
    base_network: str
    allocated: List[VlsmAllocated]
    remaining: List[VlsmRemaining]
