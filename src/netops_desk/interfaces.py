"""Lógica de dominio para Información de interfaces de red."""

from __future__ import annotations
from typing import Protocol, TypedDict
from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "InterfacesResult", "NetworkInterfacesRunner", "execute_interfaces"]

class ErrorCode:
    EXECUTION_FAILED = "execution_failed"

class InterfaceInfo(TypedDict):
    name: str
    mac_address: str | None
    ipv4: str | None
    netmask: str | None
    gateway: str | None
    dns_servers: list[str]
    is_up: bool
    speed_mbps: int

class InterfacesResult(TypedDict):
    interfaces: list[InterfaceInfo]

class NetworkInterfacesRunner(Protocol):
    def run(self) -> list[InterfaceInfo]:
        ...

def execute_interfaces(*, runner: NetworkInterfacesRunner) -> InterfacesResult:
    """Ejecuta la recolección de interfaces usando el runner inyectado."""
    try:
        interfaces = runner.run()
    except Exception as exc:
        raise DomainError(message="No se pudo obtener la información de red del sistema.", code=ErrorCode.EXECUTION_FAILED) from exc

    return {"interfaces": interfaces}