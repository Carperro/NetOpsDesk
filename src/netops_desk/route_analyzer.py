"""Lógica de dominio para el Analizador de Gateway y Rutas."""

from __future__ import annotations

import re
from typing import Protocol, TypedDict

from netops_desk.exceptions import DomainError

__all__ = [
    "DomainError",
    "ErrorCode",
    "RouteAnalyzerResult",
    "RouteRunner",
    "execute_route_analyzer",
]


class ErrorCode:
    """Códigos de error estables para la API de Route Analyzer."""
    EXECUTION_FAILED = "execution_failed"


class RouteEntry(TypedDict):
    """Representa una fila de la tabla de rutas."""
    destination: str
    netmask: str
    gateway: str
    interface: str
    metric: int


class RouteAnalyzerResult(TypedDict):
    """Resultado final del análisis de rutas."""
    default_gateway: str | None
    routes: list[RouteEntry]


class RouteExecutionResult(TypedDict):
    """Resultado crudo devuelto por el RouteRunner."""
    ipconfig_stdout: bytes
    route_stdout: bytes
    exit_code: int


class RouteRunner(Protocol):
    """Interfaz que debe implementar el adaptador de sistema operativo."""
    def run(self) -> RouteExecutionResult:
        ...


def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)


def _parse_ipconfig(output: str) -> str | None:
    """Busca el gateway por defecto en la salida de ipconfig."""
    # Acepta inglés y español. Extrae la IP que viene después de los dos puntos.
    pattern = re.compile(
        r"(?:Default Gateway|Puerta de enlace predeterminada)[^\d]*([0-9\.]+)",
        re.IGNORECASE
    )
    match = pattern.search(output)
    if match:
        return match.group(1)
    return None


def _parse_route_table(output: str) -> list[RouteEntry]:
    """Extrae la tabla de rutas IPv4 de la salida de route print -4."""
    routes = []
    # Busca líneas que tengan 3 IPs y un número al final (Destino, Máscara, Gateway, Interfaz, Métrica)
    pattern = re.compile(
        r"^\s*(\d{1,3}(?:\.\d{1,3}){3})\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3})\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3})\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3})\s+"
        r"(\d+)\s*$",
        re.MULTILINE
    )
    for match in pattern.finditer(output):
        routes.append({
            "destination": match.group(1),
            "netmask": match.group(2),
            "gateway": match.group(3),
            "interface": match.group(4),
            "metric": int(match.group(5)),
        })
    return routes


def execute_route_analyzer(*, runner: RouteRunner) -> RouteAnalyzerResult:
    """Ejecuta el analizador usando el runner inyectado."""
    result = runner.run()

    if result["exit_code"] != 0:
        raise _error(ErrorCode.EXECUTION_FAILED, "No se pudieron obtener los datos de red del sistema.")

    ipconfig_text = result["ipconfig_stdout"].decode("utf-8", errors="replace")
    route_text = result["route_stdout"].decode("utf-8", errors="replace")

    default_gateway = _parse_ipconfig(ipconfig_text)
    routes = _parse_route_table(route_text)

    # Si no hay ninguna ruta parseada, algo falló catastróficamente en el sistema
    if not routes and not default_gateway:
        raise _error(ErrorCode.EXECUTION_FAILED, "El formato de la tabla de rutas no se pudo interpretar.")

    return {
        "default_gateway": default_gateway,
        "routes": routes,
    }