"""Lógica de dominio para el Generador de Comandos."""

from __future__ import annotations
import ipaddress
import re
from typing import TypedDict
from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "CommandResult", "generate_command"]

class ErrorCode:
    INVALID_COMMAND_TYPE = "invalid_command_type"
    MISSING_TARGET = "missing_target"
    INVALID_TARGET = "invalid_target"
    INVALID_OPTION = "invalid_option"

class CommandResult(TypedDict):
    command: str
    explanation: str
    requires_admin: bool

# Reglas estrictas por comando
COMMAND_RULES = {
    "ping": {"requires_target": True, "options": ["-t", "-a"], "admin_options": []},
    "tracert": {"requires_target": True, "options": ["-d"], "admin_options": []},
    "nslookup": {"requires_target": True, "options": [], "admin_options": []},
    "ipconfig": {"requires_target": False, "options": ["/all", "/flushdns", "/release", "/renew"], "admin_options": ["/flushdns", "/release", "/renew"]},
    "netstat": {"requires_target": False, "options": ["-a", "-n", "-b"], "admin_options": ["-b"]}
}

EXPLANATIONS = {
    "ping": "Envía paquetes ICMP para probar la conectividad con un host.",
    "tracert": "Traza la ruta que siguen los paquetes hasta un destino.",
    "nslookup": "Consulta servidores DNS para resolver un dominio.",
    "ipconfig": "Muestra o gestiona la configuración de red de Windows.",
    "netstat": "Muestra conexiones de red, tablas de enrutamiento y estadísticas."
}

OPTION_EXPLANATIONS = {
    "-t": "Ping continuo (se detiene con Ctrl+C).",
    "-a": "Resuelve direcciones IP a nombres de host.",
    "-d": "No resuelve nombres de host (más rápido).",
    "/all": "Muestra toda la información detallada de las interfaces.",
    "/flushdns": "Limpia la caché de resolución de DNS.",
    "/release": "Libera la dirección IP actual.",
    "/renew": "Renueva la dirección IP vía DHCP.",
    "-b": "Muestra el ejecutable asociado a cada conexión (requiere admin)."
}

def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)

def _validate_target(target: str) -> None:
    # Validar IP o dominio (Regex simple para dominios)
    try:
        ipaddress.ip_address(target)
        return
    except ValueError:
        pass

    domain_regex = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
    if not domain_regex.match(target):
        raise _error(ErrorCode.INVALID_TARGET, "El objetivo debe ser una dirección IP o un dominio válido.")

def generate_command(*, command_type: str, target: str | None, options: list[str]) -> CommandResult:
    """Genera el comando final y su explicación."""
    
    cmd_clean = command_type.strip().lower()
    target_clean = (target or "").strip()
    
    if cmd_clean not in COMMAND_RULES:
        raise _error(ErrorCode.INVALID_COMMAND_TYPE, "El tipo de comando no está permitido.")
        
    rules = COMMAND_RULES[cmd_clean]

    # Validar Target
    if rules["requires_target"] and not target_clean:
        raise _error(ErrorCode.MISSING_TARGET, f"El comando '{cmd_clean}' requiere un objetivo (IP o dominio).")
    if target_clean:
        _validate_target(target_clean)

    # Validar Opciones
    for opt in options:
        if opt not in rules["options"]:
            raise _error(ErrorCode.INVALID_OPTION, f"La opción '{opt}' no es válida para el comando '{cmd_clean}'.")

    # Armar el comando
    cmd_parts = [cmd_clean]
    if options:
        cmd_parts.extend(options)
    if target_clean:
        cmd_parts.append(target_clean)
        
    command_str = " ".join(cmd_parts)

    # Armar la explicación
    expl_lines = [EXPLANATIONS.get(cmd_clean, "Comando de red.")]
    if options:
        expl_lines.append("\nParámetros:")
        for opt in options:
            expl_lines.append(f"  {opt}: {OPTION_EXPLANATIONS.get(opt, 'Opción del comando')}")
    
    explanation_str = "\n".join(expl_lines)

    # Verificar si requiere admin
    requires_admin = any(opt in rules["admin_options"] for opt in options)

    return {
        "command": command_str,
        "explanation": explanation_str,
        "requires_admin": requires_admin
    }