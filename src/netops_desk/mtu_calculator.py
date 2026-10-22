"""Lógica de dominio para la Calculadora MTU y fragmentación."""

from __future__ import annotations
from typing import TypedDict
from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "MtuResult", "calculate_mtu"]

class ErrorCode:
    INVALID_PARAMETER = "invalid_parameter"

class MtuResult(TypedDict):
    mtu: int
    ip_version: str
    transport: str
    tunnel: str
    mss: int
    ip_header_size: int
    transport_header_size: int
    tunnel_header_size: int
    warnings: list[str]

def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)

def calculate_mtu(
    *, mtu: int, ip_version: str, transport: str, tunnel: str
) -> MtuResult:
    """Calcula el espacio de payload disponible."""
    
    # Validaciones de Enums
    if ip_version not in ("ipv4", "ipv6"):
        raise _error(ErrorCode.INVALID_PARAMETER, "La versión IP debe ser ipv4 o ipv6.")
    if transport not in ("tcp", "udp"):
        raise _error(ErrorCode.INVALID_PARAMETER, "El transporte debe ser tcp o udp.")
    if tunnel not in ("none", "gre", "ipsec", "wireguard"):
        raise _error(ErrorCode.INVALID_PARAMETER, "El túnel no es válido.")

    # Asignación de tamaños de cabecera
    ip_h_size = 20 if ip_version == "ipv4" else 40
    transport_h_size = 20 if transport == "tcp" else 8
    
    tunnel_overheads = {
        "none": 0,
        "gre": 24,
        "ipsec": 60,
        "wireguard": 60
    }
    tunnel_h_size = tunnel_overheads[tunnel]

    total_overhead = ip_h_size + transport_h_size + tunnel_h_size
    mss = mtu - total_overhead

    warnings = []
    
    # Validaciones y advertencias
    if mss < 0:
        mss = 0
        warnings.append("packet_too_small")
        warnings.append("El MTU es demasiado pequeño para las cabeceras seleccionadas.")
    
    if mtu < 576:
        warnings.append("mtu_below_minimum")
        warnings.append("El MTU es menor al mínimo estándar de IPv4 (576 bytes).")

    return {
        "mtu": mtu,
        "ip_version": ip_version,
        "transport": transport,
        "tunnel": tunnel,
        "mss": mss,
        "ip_header_size": ip_h_size,
        "transport_header_size": transport_h_size,
        "tunnel_header_size": tunnel_h_size,
        "warnings": warnings
    }