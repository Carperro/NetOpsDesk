"""Rutas de la API para el Gestor de Direcciones IP (IPAM)."""

from fastapi import APIRouter, Depends, status

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.models.ipam import IpamInput, IpamOutput
from netops_desk.ipam import (
    create_ip, list_ips, update_ip, delete_ip
)
from netops_desk.repositories.ipam_repository import SQLiteIpamRepository

router = APIRouter(tags=["IPAM"])

def get_ipam_repo() -> SQLiteIpamRepository:
    return SQLiteIpamRepository()

@router.get("/api/v1/tools/ipam/addresses", response_model=list[IpamOutput])
async def list_ips_endpoint(repo: SQLiteIpamRepository = Depends(get_ipam_repo)):
    return list_ips(repo=repo)

@router.post("/api/v1/tools/ipam/addresses", response_model=IpamOutput, status_code=status.HTTP_201_CREATED)
async def create_ip_endpoint(
    body: IpamInput,
    _: None = Depends(require_json_content_type),
    repo: SQLiteIpamRepository = Depends(get_ipam_repo)
):
    return create_ip(repo=repo, data=body.model_dump())

@router.put("/api/v1/tools/ipam/addresses/{record_id}", response_model=IpamOutput)
async def update_ip_endpoint(
    record_id: int,
    body: IpamInput,
    _: None = Depends(require_json_content_type),
    repo: SQLiteIpamRepository = Depends(get_ipam_repo)
):
    return update_ip(repo=repo, record_id=record_id, data=body.model_dump())

@router.delete("/api/v1/tools/ipam/addresses/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ip_endpoint(
    record_id: int,
    repo: SQLiteIpamRepository = Depends(get_ipam_repo)
):
    delete_ip(repo=repo, record_id=record_id)
    return None