"""Rutas de la API para el Inventario de Dispositivos."""

from fastapi import APIRouter, Depends, status

from netops_desk.api.dependencies import require_json_content_type
from netops_desk.api.models.inventory import DeviceInput, DeviceOutput
from netops_desk.inventory import (
    create_device, list_devices, update_device, delete_device
)
from netops_desk.repositories.inventory_repository import SQLiteInventoryRepository

router = APIRouter(tags=["Inventory"])

# Dependencia para inyectar el repositorio
def get_inventory_repo() -> SQLiteInventoryRepository:
    return SQLiteInventoryRepository()

@router.get("/api/v1/tools/inventory/devices", response_model=list[DeviceOutput])
async def list_devices_endpoint(repo: SQLiteInventoryRepository = Depends(get_inventory_repo)):
    return list_devices(repo=repo)

@router.post("/api/v1/tools/inventory/devices", response_model=DeviceOutput, status_code=status.HTTP_201_CREATED)
async def create_device_endpoint(
    body: DeviceInput,
    _: None = Depends(require_json_content_type),
    repo: SQLiteInventoryRepository = Depends(get_inventory_repo)
):
    # El DomainError asciende solo al handler global
    return create_device(repo=repo, data=body.model_dump())

@router.put("/api/v1/tools/inventory/devices/{device_id}", response_model=DeviceOutput)
async def update_device_endpoint(
    device_id: int,
    body: DeviceInput,
    _: None = Depends(require_json_content_type),
    repo: SQLiteInventoryRepository = Depends(get_inventory_repo)
):
    return update_device(repo=repo, device_id=device_id, data=body.model_dump())

@router.delete("/api/v1/tools/inventory/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device_endpoint(
    device_id: int,
    repo: SQLiteInventoryRepository = Depends(get_inventory_repo)
):
    delete_device(repo=repo, device_id=device_id)
    return None