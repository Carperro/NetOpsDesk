"""Lógica de dominio para la herramienta Ping.

Valida el host, invoca a un PingRunner inyectado y calcula las
estadísticas. No depende de FastAPI, Pydantic ni subprocess.
"""

from __future__ import annotations

import ipaddress
import re
from typing import Protocol, TypedDict

from netops_desk.exceptions import DomainError


__all__ = [
    "DomainError",
    "ErrorCode",
    "PingExecutionResult",
    "PingResult",
    "PingRunner",
    "execute_ping",
]


class ErrorCode:
    """Códigos de error estables del contrato de la API Ping."""

    INVALID_HOST = "invalid_host"
    INVALID_COUNT = "invalid_count"
    PING_TIMEOUT = "ping_timeout"
    EXECUTION_FAILED = "execution_failed"


class PingResponse(TypedDict):
    """Respuesta individual de un paquete ICMP."""

    seq: int
    time_ms: float


class PingResult(TypedDict):
    """Resultado final del cálculo de ping."""

    host: str
    resolved_ip: str
    packets_sent: int
    packets_received: int
    packet_loss_percent: float
    min_ms: float | None
    max_ms: float | None
    avg_ms: float | None
    responses: list[PingResponse]


class PingExecutionResult(TypedDict):
    """Resultado estructurado que devuelve el PingRunner."""

    exit_code: int
    stdout: bytes
    stderr: bytes
    timed_out: bool


class PingRunner(Protocol):
    """Interfaz que debe implementar el adaptador de sistema operativo."""

    def run(self, host: str, count: int) -> PingExecutionResult:
        """Ejecuta el ping y devuelve el resultado crudo."""
        ...


def _error(code: str, message: str) -> DomainError:
    """Crea un error de dominio con el código y el mensaje indicados."""
    return DomainError(message=message, code=code)


def _validate_host(host: str) -> None:
    """Valida que el host sea una IP o un dominio seguro (sin inyección)."""
    if not host or len(host) > 253:
        raise _error(ErrorCode.INVALID_HOST, "El host no puede estar vacío ni superar los 253 caracteres.")

    # Intentar parsear como IPv4 o IPv6 primero
    try:
        ipaddress.ip_address(host)
        return
    except ValueError:
        pass

    # Validación estricta de dominio (RFC 1123)
    # Solo letras, números, guiones y puntos. Sin espacios ni caracteres de shell.
    hostname_pattern = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
    if not hostname_pattern.match(host):
        raise _error(
            ErrorCode.INVALID_HOST,
            "El host debe ser una dirección IPv4, IPv6 o un nombre de dominio válido. No se permiten caracteres especiales.",
        )


def _validate_count(count: int) -> None:
    """Valida que la cantidad de paquetes esté en el rango permitido."""
    if not isinstance(count, int) or isinstance(count, bool):
        raise _error(ErrorCode.INVALID_COUNT, "La cantidad debe ser un número entero.")
    if count < 1 or count > 10:
        raise _error(ErrorCode.INVALID_COUNT, "La cantidad debe estar entre 1 y 10.")


def _extract_ip(output: str) -> str:
    """Extrae la primera IP válida del texto de salida de Windows."""
    # Busca secuencias que parezcan IPv4 o IPv6
    candidates = re.findall(r"[a-fA-F0-9:\.]+", output)
    for c in candidates:
        try:
            ip = ipaddress.ip_address(c)
            return str(ip)
        except ValueError:
            continue
    return ""


def _parse_times(output: str) -> list[float]:
    """Extrae los tiempos de respuesta (RTT) en milisegundos del texto."""
    times = []
    # Atrapa el operador en el grupo 1 y el número en el grupo 2
    pattern = re.compile(r"(?:time|tiempo)([=<])(\d*\.?\d*)ms", re.IGNORECASE)
    
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            operator = match.group(1)
            val_str = match.group(2)
            
            if operator == "<":
                # Convención contractual: "<1ms" se reporta como 0.0
                times.append(0.0)
            else:
                times.append(float(val_str) if val_str else 0.0)
                
    return times


def execute_ping(*, host: str, count: int = 4, runner: PingRunner) -> PingResult:
    """Ejecuta el ping usando el runner inyectado y calcula las estadísticas."""
    _validate_host(host)
    _validate_count(count)

    result = runner.run(host, count)

    if result["timed_out"]:
        raise _error(ErrorCode.PING_TIMEOUT, "La ejecución del ping superó el tiempo límite.")

    # Decodificamos con errors="replace" por la localización de Windows
    stdout_text = result["stdout"].decode("utf-8", errors="replace")
    stderr_text = result["stderr"].decode("utf-8", errors="replace")

    resolved_ip = _extract_ip(stdout_text)

    # Si no hay IP y el código de salida no es el esperado, fue un fallo real
    if not resolved_ip:
        if result["exit_code"] not in (0, 1):
            raise _error(ErrorCode.EXECUTION_FAILED, "No se pudo ejecutar la herramienta ping o no devolvió un resultado válido.")
        # Si no hay IP pero exit_code es 1, puede ser un fallo total de DNS
        resolved_ip = host

    times = _parse_times(stdout_text)
    packets_received = len(times)
    packets_sent = count
    packet_loss = ((packets_sent - packets_received) / packets_sent) * 100.0

    responses: list[PingResponse] = []
    for i, t in enumerate(times, start=1):
        responses.append({"seq": i, "time_ms": t})

    if times:
        min_ms = min(times)
        max_ms = max(times)
        avg_ms = sum(times) / len(times)
    else:
        min_ms = None
        max_ms = None
        avg_ms = None

    return {
        "host": host,
        "resolved_ip": resolved_ip,
        "packets_sent": packets_sent,
        "packets_received": packets_received,
        "packet_loss_percent": packet_loss,
        "min_ms": min_ms,
        "max_ms": max_ms,
        "avg_ms": avg_ms,
        "responses": responses,
    }