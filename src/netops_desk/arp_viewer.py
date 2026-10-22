"""Lógica de dominio para el Visor de Caché ARP."""

from __future__ import annotations

import re
from typing import Protocol, TypedDict

from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "ArpResult", "ArpRunner", "execute_arp_viewer"]

class ErrorCode:
    EXECUTION_FAILED = "execution_failed"

class ArpEntry(TypedDict):
    interface_ip: str
    ip_address: str
    mac_address: str
    entry_type: str

class ArpResult(TypedDict):
    entries: list[ArpEntry]

class ArpExecutionResult(TypedDict):
    exit_code: int
    stdout: bytes
    stderr: bytes

class ArpRunner(Protocol):
    def run(self) -> ArpExecutionResult:
        ...

def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)

def _parse_arp(output: str) -> list[ArpEntry]:
    entries = []
    current_interface = None

    iface_pattern = re.compile(r"(?:Interfaz|Interface):\s*(\d{1,3}(?:\.\d{1,3}){3})")
    ip_pattern = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
    mac_pattern = re.compile(r"^([0-9a-fA-F:\-]{17})$")

    for line in output.splitlines():
        iface_match = iface_pattern.search(line)
        if iface_match:
            current_interface = iface_match.group(1)
            continue

        if current_interface:
            parts = line.split()
            if len(parts) >= 3:
                ip = parts[0]
                mac = parts[1]
                entry_type_raw = parts[2].lower()

                if ip_pattern.match(ip) and mac_pattern.match(mac):
                    if "est" in entry_type_raw or "stat" in entry_type_raw:
                        entry_type = "static"
                    else:
                        entry_type = "dynamic"

                    entries.append({
                        "interface_ip": current_interface,
                        "ip_address": ip,
                        "mac_address": mac.lower().replace(":", "-"),
                        "entry_type": entry_type
                    })
                    if len(entries) >= 500:
                        break
    return entries

def execute_arp_viewer(*, runner: ArpRunner) -> ArpResult:
    result = runner.run()
    if result["exit_code"] != 0:
        raise _error(ErrorCode.EXECUTION_FAILED, "No se pudo ejecutar el comando ARP del sistema.")

    # ACÁ ESTÁ LA MAGIA: codificamos explícitamente para Windows en español
    output = result["stdout"].decode("cp850", errors="replace")
    entries = _parse_arp(output)
    return {"entries": entries}
