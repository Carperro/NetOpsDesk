"""Lógica de dominio para la Prueba de puertos TCP."""

from __future__ import annotations

import ipaddress
import re
from typing import Protocol, TypedDict

from netops_desk.exceptions import DomainError


__all__ = [
    "DomainError",
    "ErrorCode",
    "TcpExecutionResult",
    "TcpResult",
    "TcpRunner",
    "execute_tcp_test",
]


class ErrorCode:
    """Códigos de error estables de la API TCP Test."""
    INVALID_HOST = "invalid_host"
    INVALID_PORT = "invalid_port"
    INVALID_TIMEOUT = "invalid_timeout"
    HOST_UNREACHABLE = "host_unreachable"
    TCP_TIMEOUT = "tcp_timeout"
    EXECUTION_FAILED = "execution_failed"


class TcpResult(TypedDict):
    """Resultado final de la prueba TCP."""
    host: str
    port: int
    status: str  # "open", "closed", "filtered"
    time_ms: float


class TcpExecutionResult(TypedDict):
    """Resultado estructurado que devuelve el TcpRunner."""
    status: str
    time_ms: float


class TcpRunner(Protocol):
    """Interfaz que debe implementar el adaptador de socket."""
    def run(self, host: str, port: int, timeout_ms: int) -> TcpExecutionResult:
        ...


def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)


def _validate_host(host: str) -> None:
    if not host or len(host) > 253:
        raise _error(ErrorCode.INVALID_HOST, "El host no puede estar vacío.")
    try:
        ipaddress.ip_address(host)
        return
    except ValueError:
        pass

    hostname_pattern = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
    if not hostname_pattern.match(host):
        raise _error(ErrorCode.INVALID_HOST, "El host debe ser una dirección IP o dominio válido.")


def _validate_port(port: int) -> None:
    if not isinstance(port, int) or isinstance(port, bool):
        raise _error(ErrorCode.INVALID_PORT, "El puerto debe ser un número entero.")
    if port < 1 or port > 65535:
        raise _error(ErrorCode.INVALID_PORT, "El puerto debe estar entre 1 y 65535.")


def _validate_timeout(timeout_ms: int) -> None:
    if not isinstance(timeout_ms, int) or isinstance(timeout_ms, bool):
        raise _error(ErrorCode.INVALID_TIMEOUT, "El timeout debe ser un número entero.")
    if timeout_ms < 500 or timeout_ms > 10000:
        raise _error(ErrorCode.INVALID_TIMEOUT, "El timeout debe estar entre 500 y 10000 ms.")


def execute_tcp_test(*, host: str, port: int, timeout_ms: int = 3000, runner: TcpRunner) -> TcpResult:
    """Ejecuta la prueba TCP usando el runner inyectado."""
    _validate_host(host)
    _validate_port(port)
    _validate_timeout(timeout_ms)

    result = runner.run(host, port, timeout_ms)

    return {
        "host": host,
        "port": port,
        "status": result["status"],
        "time_ms": result["time_ms"],
    }