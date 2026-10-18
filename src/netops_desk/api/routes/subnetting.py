from fastapi import APIRouter, Depends
from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.models import (
    SubnettingByCountInput, 
    SubnettingByHostsInput, 
    SubnettingOutput, 
    SubnetResult
)
from netops_desk.subnetting import (
    calculate_subnets_by_count, 
    calculate_subnets_by_hosts
)

router = APIRouter(prefix="/api/v1/tools/subnetting", tags=["Subnetting"])

def format_subnet(subnet) -> SubnetResult:
    """Convierte un objeto IPv4Network a nuestro modelo Pydantic para enviar como JSON."""
    # Si la red es muy grande (ej. /8), list(subnet.hosts()) consumiría mucha memoria.
    # Calculamos el primer y último host matemáticamente de forma segura.
    first_host = str(subnet.network_address + 1) if subnet.num_addresses > 2 else None
    last_host = str(subnet.broadcast_address - 1) if subnet.num_addresses > 2 else None
    
    return SubnetResult(
        network=str(subnet.network_address),
        broadcast=str(subnet.broadcast_address),
        prefixlen=subnet.prefixlen,
        netmask=str(subnet.netmask),
        first_host=first_host,
        last_host=last_host,
        total_addresses=subnet.num_addresses
    )

@router.post("/by-count", response_model=SubnettingOutput)
async def subnet_by_count(
    payload: SubnettingByCountInput,
    _: None = Depends(require_json_content_type),
):
    result = calculate_subnets_by_count(payload.network_cidr, payload.subnet_count)
    formatted_subnets = [format_subnet(s) for s in result["subnets"]]
    return SubnettingOutput(
        subnets=formatted_subnets,
        was_normalized=result["was_normalized"],
        original_network=result["original_network"]
    )

@router.post("/by-hosts", response_model=SubnettingOutput)
async def subnet_by_hosts(
    payload: SubnettingByHostsInput,
    _: None = Depends(require_json_content_type),
):
    result = calculate_subnets_by_hosts(payload.network_cidr, payload.required_hosts)
    formatted_subnets = [format_subnet(s) for s in result["subnets"]]
    return SubnettingOutput(
        subnets=formatted_subnets,
        was_normalized=result["was_normalized"],
        original_network=result["original_network"],
        new_prefix=result["new_prefix"],
        usable_hosts_per_subnet=result["usable_hosts_per_subnet"]
    )
