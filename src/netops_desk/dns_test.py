"""Lógica de dominio para la herramienta de Diagnóstico DNS."""

from __future__ import annotations

import ipaddress
import re
from typing import Protocol, TypedDict

from netops_desk.exceptions import DomainError

__all__ = [
    "DomainError",
    "ErrorCode",
    "DnsExecutionResult",
    "DnsResult",
    "DnsRunner",
    "execute_dns_test",
]


class ErrorCode:
    """Códigos de error estables para la API DNS."""
    INVALID_DOMAIN = "invalid_domain"
    INVALID_RECORD_TYPE = "invalid_record_type"
    INVALID_RESOLVER = "invalid_resolver"
    DNS_TIMEOUT = "dns_timeout"
    EXECUTION_FAILED = "execution_failed"


class DnsResult(TypedDict):
    """Resultado final de la consulta DNS."""
    domain: str
    record_type: str
    resolver: str
    status: str  # "success" o "nxdomain"
    time_ms: float
    records: list[str]


class DnsExecutionResult(TypedDict):
    """Resultado estructurado que devuelve el DnsRunner."""
    status: str
    time_ms: float
    records: list[str]


class DnsRunner(Protocol):
    """Interfaz que debe implementar el adaptador de dnspython."""
    def run(self, domain: str, record_type: str, resolver: str | None) -> DnsExecutionResult:
        ...


def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)


def _validate_domain(domain: str) -> None:
    if not domain or len(domain) > 253:
        raise _error(ErrorCode.INVALID_DOMAIN, "El dominio no puede estar vacío o superar los 253 caracteres.")
    
    domain_pattern = re.compile(r"^([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
    if not domain_pattern.match(domain):
        raise _error(ErrorCode.INVALID_DOMAIN, "El formato del dominio no es válido.")


def _validate_record_type(record_type: str) -> None:
    valid_types = {"A", "AAAA", "MX", "TXT", "NS", "CNAME"}
    if record_type.upper() not in valid_types:
        raise _error(
            ErrorCode.INVALID_RECORD_TYPE,
            f"El tipo de registro debe ser uno de: {', '.join(valid_types)}."
        )


def _validate_resolver(resolver: str | None) -> None:
    if not resolver:
        return
    try:
        ipaddress.ip_address(resolver)
    except ValueError:
        raise _error(ErrorCode.INVALID_RESOLVER, "La IP del resolver no es válida.")


def execute_dns_test(
    *, domain: str, record_type: str, resolver: str | None = None, runner: DnsRunner
) -> DnsResult:
    """Ejecuta la consulta DNS usando el runner inyectado."""
    domain = domain.strip().lower()
    record_type = record_type.strip().upper()
    
    _validate_domain(domain)
    _validate_record_type(record_type)
    _validate_resolver(resolver)

    result = runner.run(domain, record_type, resolver)

    return {
        "domain": domain,
        "record_type": record_type,
        "resolver": resolver if resolver else "system",
        "status": result["status"],
        "time_ms": result["time_ms"],
        "records": result["records"],
    }