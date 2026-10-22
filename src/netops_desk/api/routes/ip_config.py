"""Rutas de la API para Asistente de Configuración IP."""

from fastapi import APIRouter, Depends
from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.models.ip_config import IpConfigInput, IpConfigOutput
from netops_desk.ip_config import generate_command

router = APIRouter(tags=["IP Config"])

@router.post(
    "/api/v1/tools/ip-config/execute",
    response_model=IpConfigOutput,
    summary="Genera comandos para configurar IP",
)
async def execute_ip_config_endpoint(
    body: IpConfigInput,
    _: None = Depends(require_json_content_type),
) -> IpConfigOutput:
    
    result = generate_command(
        action=body.action,
        interface_name=body.interface_name,
        ip=body.ip,
        mask=body.mask,
        gateway=body.gateway,
        dns_ip=body.dns_ip,
    )
    return IpConfigOutput(**result)