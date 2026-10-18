from pydantic import BaseModel, ConfigDict, Field
from typing import List

class SubnettingByCountInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    network_cidr: str = Field(..., description="Red base, ej: 192.168.1.0/24")
    subnet_count: int = Field(..., gt=0, description="Cantidad de subredes deseadas")

class SubnettingByHostsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    network_cidr: str = Field(..., description="Red base, ej: 192.168.1.0/24")
    required_hosts: int = Field(..., gt=0, description="Hosts necesarios por subred")

class SubnetResult(BaseModel):
    network: str
    broadcast: str
    prefixlen: int
    netmask: str
    first_host: str | None
    last_host: str | None
    total_addresses: int

class SubnettingOutput(BaseModel):
    subnets: List[SubnetResult]
    was_normalized: bool
    original_network: str
    # Campos opcionales que solo se usan en el modo B
    new_prefix: int | None = None
    usable_hosts_per_subnet: int | None = None
