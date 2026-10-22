"""Lógica de dominio para el Visor de Tabla de Rutas."""

from __future__ import annotations
import ipaddress
import re
from typing import Protocol, TypedDict
from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "RouteTableResult", "RouteTableRunner", "execute_route_table"]

class ErrorCode:
    EXECUTION_FAILED = "execution_failed"

class RouteEntry(TypedDict):
    destination: str
    netmask: str
    gateway: str
    interface: str
    metric: int

class RouteTableResult(TypedDict):
    routes: list[RouteEntry]

class RouteExecutionResult(TypedDict):
    exit_code: int
    stdout: bytes
    stderr: bytes

class RouteTableRunner(Protocol):
    def run(self) -> RouteExecutionResult:
        ...

def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)

def _parse_routes(output: str) -> list[RouteEntry]:
    routes = []
    # Captura exactamente 4 IPs y un número entero al final
    pattern = re.compile(
        r"^\s*(\d{1,3}(?:\.\d{1,3}){3})\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3})\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3})\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3})\s+"
        r"(\d+)\s*$",
        re.MULTILINE
    )
    for match in pattern.finditer(output):
        dest, netmask, gw, iface, metric = match.groups()
        # Validar IPs con ipaddress para evitar falsos positivos
        try:
            ipaddress.IPv4Address(dest)
            ipaddress.IPv4Address(netmask)
            ipaddress.IPv4Address(gw)
            ipaddress.IPv4Address(iface)
            
            routes.append({
                "destination": dest,
                "netmask": netmask,
                "gateway": gw,
                "interface": iface,
                "metric": int(metric),
            })
        except ValueError:
            pass # Ignorar si no es IPv4 válida
    return routes

def execute_route_table(*, runner: RouteTableRunner) -> RouteTableResult:
    result = runner.run()
    if result["exit_code"] != 0:
        raise _error(ErrorCode.EXECUTION_FAILED, "No se pudo obtener la tabla de rutas del sistema.")
    
    # cp850 suele ser el encoding por defecto de la consola de Windows
    output = result["stdout"].decode("cp850", errors="replace")
    routes = _parse_routes(output)
    return {"routes": routes}