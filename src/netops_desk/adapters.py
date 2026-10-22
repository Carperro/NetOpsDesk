"""Lógica de dominio para el Estado de Adaptadores."""

from __future__ import annotations
from typing import Protocol, TypedDict
from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "AdaptersResult", "AdaptersRunner", "execute_adapters"]

class ErrorCode:
    EXECUTION_FAILED = "execution_failed"

class AdapterInfo(TypedDict):
    name: str
    is_up: bool
    speed_mbps: int
    mtu: int
    is_multicast: bool

class AdaptersResult(TypedDict):
    adapters: list[AdapterInfo]

class AdaptersRunner(Protocol):
    def run(self) -> list[AdapterInfo]:
        ...

def execute_adapters(*, runner: AdaptersRunner) -> AdaptersResult:
    """Ejecuta la recolección de adaptadores usando el runner inyectado."""
    try:
        adapters = runner.run()
    except Exception as exc:
        raise DomainError(
            message="No se pudo obtener la información de los adaptadores.",
            code=ErrorCode.EXECUTION_FAILED
        ) from exc

    return {"adapters": adapters}