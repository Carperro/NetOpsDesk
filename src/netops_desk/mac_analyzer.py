"""Lógica de dominio para el Analizador de Direcciones MAC."""

from __future__ import annotations
import re
from typing import Protocol, TypedDict
from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "MacResult", "MacVendorLookupRunner", "execute_mac_analyzer"]

class ErrorCode:
    INVALID_MAC = "invalid_mac"
    EXECUTION_FAILED = "execution_failed"

class MacResult(TypedDict):
    mac_original: str
    mac_normalized: str
    vendor: str

class MacVendorLookupRunner(Protocol):
    def lookup(self, mac: str) -> str:
        """Devuelve el fabricante o 'Desconocido'."""
        ...

def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)

def execute_mac_analyzer(*, mac: str, runner: MacVendorLookupRunner) -> MacResult:
    """Valida, normaliza y busca el fabricante de una MAC."""
    mac_clean = mac.strip()
    
    # Validar formato: 6 pares hexadecimales separados por : o -
    pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
    if not pattern.match(mac_clean):
        raise _error(ErrorCode.INVALID_MAC, "El formato de la dirección MAC no es válido. Usá 6 pares hexadecimales (ej. 00:1A:2B:3C:4D:5E).")

    # Normalizar a minúsculas con dos puntos
    normalized = mac_clean.lower().replace("-", ":")

    try:
        vendor = runner.lookup(normalized)
    except Exception as exc:
        raise _error(ErrorCode.EXECUTION_FAILED, "No se pudo consultar la base de datos de fabricantes.") from exc

    return {
        "mac_original": mac_clean,
        "mac_normalized": normalized,
        "vendor": vendor
    }