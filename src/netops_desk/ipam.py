"""Lógica de dominio para el Gestor de Direcciones IP (IPAM)."""

from __future__ import annotations
import ipaddress
from netops_desk.exceptions import DomainError
from netops_desk.repositories.ipam_repository import IpamRepository, IpamRecord

__all__ = [
    "DomainError", "ErrorCode", "IpamRecord", "IpamRepository",
    "create_ip", "list_ips", "update_ip", "delete_ip"
]

class ErrorCode:
    INVALID_IP = "invalid_ip"
    INVALID_STATUS = "invalid_status"
    NOT_FOUND = "not_found"
    # Nota: "duplicate_ip" es lanzado directamente por el repositorio

VALID_STATUSES = ("available", "assigned", "reserved")

def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)

def _validate_data(data: dict) -> None:
    ip = data.get("ip_address", "").strip()
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        raise _error(ErrorCode.INVALID_IP, "La dirección IP no es una IPv4 válida.")

    status = data.get("status", "").strip().lower()
    if status not in VALID_STATUSES:
        raise _error(
            ErrorCode.INVALID_STATUS, 
            f"El estado debe ser uno de: {', '.join(VALID_STATUSES)}."
        )

def create_ip(*, repo: IpamRepository, data: dict) -> IpamRecord:
    _validate_data(data)
    
    record: IpamRecord = {
        "id": None,
        "ip_address": data["ip_address"].strip(),
        "status": data["status"].strip().lower(),
        "assigned_to": data.get("assigned_to", "").strip(),
        "notes": data.get("notes", "").strip(),
    }
    return repo.create(record)

def list_ips(*, repo: IpamRepository) -> list[IpamRecord]:
    return repo.list_all()

def update_ip(*, repo: IpamRepository, record_id: int, data: dict) -> IpamRecord:
    _validate_data(data)
    
    existing = repo.get_by_id(record_id)
    if not existing:
        raise _error(ErrorCode.NOT_FOUND, "Registro IP no encontrado.")
        
    record: IpamRecord = {
        "id": record_id,
        "ip_address": data["ip_address"].strip(),
        "status": data["status"].strip().lower(),
        "assigned_to": data.get("assigned_to", "").strip(),
        "notes": data.get("notes", "").strip(),
    }
    return repo.update(record_id, record)

def delete_ip(*, repo: IpamRepository, record_id: int) -> bool:
    if not repo.get_by_id(record_id):
        raise _error(ErrorCode.NOT_FOUND, "Registro IP no encontrado.")
    return repo.delete(record_id)