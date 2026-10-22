"""Lógica de dominio para la herramienta Traceroute.

Valida el host y max_hops, invoca un TracerouteRunner inyectado y parsea
la salida cruda para estructurar los saltos.
"""

from __future__ import annotations

import ipaddress
import re
from typing import Protocol, TypedDict

from netops_desk.exceptions import DomainError


__all__ = [
    "DomainError",
    "ErrorCode",
    "TracerouteExecutionResult",
    "TracerouteResult",
    "TracerouteRunner",
    "execute_traceroute",
]


class ErrorCode:
    """Códigos de error estables del contrato de la API Traceroute."""

    INVALID_HOST = "invalid_host"
    INVALID_MAX_HOPS = "invalid_max_hops"
    TRACEROUTE_TIMEOUT = "traceroute_timeout"
    EXECUTION_FAILED = "execution_failed"


class TracerouteHop(TypedDict):
    """Representa un salto en la ruta."""
    hop_number: int
    ip: str | None
    times_ms: list[float]


class TracerouteResult(TypedDict):
    """Resultado final de la ejecución de traceroute."""
    host: str
    resolved_ip: str
    hops: list[TracerouteHop]


class TracerouteExecutionResult(TypedDict):
    """Resultado estructurado que devuelve el TracerouteRunner."""
    exit_code: int
    stdout: bytes
    stderr: bytes
    timed_out: bool


class TracerouteRunner(Protocol):
    """Interfaz que debe implementar el adaptador de sistema operativo."""

    def run(self, host: str, max_hops: int) -> TracerouteExecutionResult:
        """Ejecuta tracert y devuelve el resultado crudo."""
        ...


def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)


def _validate_host(host: str) -> None:
    if not host or len(host) > 253:
        raise _error(ErrorCode.INVALID_HOST, "El host no puede estar vacío ni superar los 253 caracteres.")
    try:
        ipaddress.ip_address(host)
        return
    except ValueError:
        pass

    hostname_pattern = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
    if not hostname_pattern.match(host):
        raise _error(
            ErrorCode.INVALID_HOST,
            "El host debe ser una dirección IPv4, IPv6 o un nombre de dominio válido.",
        )


def _validate_max_hops(max_hops: int) -> None:
    if not isinstance(max_hops, int) or isinstance(max_hops, bool):
        raise _error(ErrorCode.INVALID_MAX_HOPS, "El límite de saltos debe ser un número entero.")
    if max_hops < 1 or max_hops > 30:
        raise _error(ErrorCode.INVALID_MAX_HOPS, "El límite de saltos debe estar entre 1 y 30.")


def _parse_tracert_output(output: str) -> list[TracerouteHop]:
    """Extrae los saltos del texto de salida de tracert.exe."""
    hops = []
    # Busca líneas que empiecen con un número (el número de salto)
    hop_pattern = re.compile(r"^\s*(\d+)\s+(.*)$")

    for line in output.splitlines():
        match = hop_pattern.match(line)
        if not match:
            continue
        
        hop_number = int(match.group(1))
        content = match.group(2)

        # Extraer los tiempos. Acepta "12 ms" o "<1 ms"
        times_str = re.findall(r"(<\d+|\d+)\s*ms", content, re.IGNORECASE)
        times_ms = []
        for t in times_str:
            if t.startswith("<"):
                times_ms.append(0.0)
            else:
                times_ms.append(float(t))

        # Extraer IP (IPv4 o IPv6) del final de la línea
        ip_match = re.search(r"([0-9a-fA-F\.:]+)\s*$", content)
        ip = ip_match.group(1) if ip_match else None

        # Validar que lo extraído sea una IP real (por si atrapó basura)
        if ip:
            try:
                ip = str(ipaddress.ip_address(ip))
            except ValueError:
                ip = None

        hops.append({
            "hop_number": hop_number,
            "ip": ip,
            "times_ms": times_ms,
        })

    return hops


def _extract_resolved_ip(output: str, default_host: str) -> str:
    """Intenta adivinar la IP final (destino) desde la cabecera de tracert."""
    # Busca la línea tipo: "Tracing route to google.com [142.250.78.142]"
    match = re.search(r"\[([0-9a-fA-F\.:]+)\]", output)
    if match:
        try:
            return str(ipaddress.ip_address(match.group(1)))
        except ValueError:
            pass
    return default_host


def execute_traceroute(*, host: str, max_hops: int = 15, runner: TracerouteRunner) -> TracerouteResult:
    """Ejecuta traceroute usando el runner inyectado."""
    _validate_host(host)
    _validate_max_hops(max_hops)

    result = runner.run(host, max_hops)

    if result["timed_out"]:
        raise _error(ErrorCode.TRACEROUTE_TIMEOUT, "La ejecución de traceroute superó el tiempo límite.")

    stdout_text = result["stdout"].decode("utf-8", errors="replace")
    
    if result["exit_code"] not in (0, 1):
         raise _error(ErrorCode.EXECUTION_FAILED, "No se pudo ejecutar la herramienta traceroute.")

    hops = _parse_tracert_output(stdout_text)
    resolved_ip = _extract_resolved_ip(stdout_text, host)

    return {
        "host": host,
        "resolved_ip": resolved_ip,
        "hops": hops,
    }