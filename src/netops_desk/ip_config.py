"""Lógica de dominio para el Asistente de Configuración IP."""

from __future__ import annotations
import ipaddress
from typing import TypedDict, Literal
from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "IpConfigResult", "generate_command"]

class ErrorCode:
    INVALID_ACTION = "invalid_action"
    MISSING_FIELDS = "missing_fields"
    INVALID_IP_FORMAT = "invalid_ip_format"
    INVALID_INTERFACE_NAME = "invalid_interface_name"

ActionType = Literal["renew_dhcp", "set_dhcp", "set_static", "set_dns"]

class IpConfigResult(TypedDict):
    action: str
    command: str
    explanation: str

def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)

def _validate_ip(ip: str | None, field_name: str) -> str:
    if not ip:
        raise _error(ErrorCode.MISSING_FIELDS, f"Falta el campo '{field_name}'.")
    try:
        return str(ipaddress.IPv4Address(ip))
    except ValueError:
        raise _error(ErrorCode.INVALID_IP_FORMAT, f"El campo '{field_name}' no es una IPv4 válida.")

def _validate_interface(name: str | None) -> str:
    if not name:
        raise _error(ErrorCode.MISSING_FIELDS, "Falta el nombre de la interfaz.")
    # Prevenir inyección de comandos en la consola al copiar/pegar
    if any(c in name for c in ['"', '&', '|', ';', '<', '>']):
        raise _error(ErrorCode.INVALID_INTERFACE_NAME, "El nombre de la interfaz contiene caracteres no permitidos.")
    return name

def generate_command(
    *, action: str, interface_name: str | None = None, ip: str | None = None,
    mask: str | None = None, gateway: str | None = None, dns_ip: str | None = None
) -> IpConfigResult:
    """Genera el comando de Windows y su explicación sin ejecutarlo."""
    
    if action not in ("renew_dhcp", "set_dhcp", "set_static", "set_dns"):
        raise _error(ErrorCode.INVALID_ACTION, "La acción solicitada no es válida.")

    iface = _validate_interface(interface_name)

    if action == "renew_dhcp":
        cmd = f'ipconfig /renew "{iface}"'
        exp = f"Este comando solicita una nueva dirección IP al servidor DHCP para la interfaz '{iface}'. Útil si tenés problemas de conexión y la IP está en conflicto o vencida."
    
    elif action == "set_dhcp":
        cmd = f'netsh interface ip set address name="{iface}" source=dhcp'
        exp = f"Este comando configura la interfaz '{iface}' para que obtenga su dirección IP automáticamente de un servidor DHCP."
        
    elif action == "set_static":
        valid_ip = _validate_ip(ip, "ip")
        valid_mask = _validate_ip(mask, "mask")
        valid_gw = _validate_ip(gateway, "gateway")
        cmd = f'netsh interface ip set address name="{iface}" static {valid_ip} {valid_mask} {valid_gw}'
        exp = f"Este comando asigna la IP estática {valid_ip} a la interfaz '{iface}'. Asegurate de que la IP no esté en uso y sea de la misma subred que tu Gateway."

    elif action == "set_dns":
        valid_dns = _validate_ip(dns_ip, "dns_ip")
        cmd = f'netsh interface ip set dns name="{iface}" static {valid_dns}'
        exp = f"Este comando configura el servidor DNS estático {valid_dns} para la interfaz '{iface}'."
    else:
        raise _error(ErrorCode.INVALID_ACTION, "Acción no implementada.")

    return {
        "action": action,
        "command": cmd,
        "explanation": exp + " (Recordá ejecutar la consola como Administrador)."
    }