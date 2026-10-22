"""Lógica de dominio para el Inventario de Dispositivos."""

from __future__ import annotations
import ipaddress
from typing import TypedDict
from netops_desk.exceptions import DomainError
from netops_desk.repositories.inventory_repository import InventoryRepository, Device

__all__ = [
    "DomainError", "ErrorCode", "Device", "InventoryRepository",
    "create_device", "list_devices", "update_device", "delete_device"
]

class ErrorCode:
    INVALID_NAME = "invalid_name"
    INVALID_IP = "invalid_ip"
    NOT_FOUND = "not_found"

def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)

def _validate_device_data(data: dict) -> None:
    name = data.get("name", "").strip()
    if not name:
        raise _error(ErrorCode.INVALID_NAME, "El nombre del dispositivo es obligatorio.")
    
    ip = data.get("ip_address", "").strip()
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        raise _error(ErrorCode.INVALID_IP, "La dirección IP no es una IPv4 válida.")

def create_device(*, repo: InventoryRepository, data: dict) -> Device:
    _validate_device_data(data)
    
    device: Device = {
        "id": None,
        "name": data["name"].strip(),
        "ip_address": data["ip_address"].strip(),
        "device_type": data.get("device_type", "").strip(),
        "location": data.get("location", "").strip(),
        "notes": data.get("notes", "").strip(),
    }
    return repo.create(device)

def list_devices(*, repo: InventoryRepository) -> list[Device]:
    return repo.list_all()

def update_device(*, repo: InventoryRepository, device_id: int, data: dict) -> Device:
    _validate_device_data(data)
    
    existing = repo.get_by_id(device_id)
    if not existing:
        raise _error(ErrorCode.NOT_FOUND, "Dispositivo no encontrado.")
        
    device: Device = {
        "id": device_id,
        "name": data["name"].strip(),
        "ip_address": data["ip_address"].strip(),
        "device_type": data.get("device_type", "").strip(),
        "location": data.get("location", "").strip(),
        "notes": data.get("notes", "").strip(),
    }
    return repo.update(device_id, device)

def delete_device(*, repo: InventoryRepository, device_id: int) -> bool:
    if not repo.get_by_id(device_id):
        raise _error(ErrorCode.NOT_FOUND, "Dispositivo no encontrado.")
    return repo.delete(device_id)