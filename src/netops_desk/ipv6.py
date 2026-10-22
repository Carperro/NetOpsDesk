"""Cálculos puros del dominio IPv6/CIDR para NetOps Desk.

Calcula información de una dirección y un prefijo IPv6, incluida la red,
la última dirección del bloque, la cantidad de direcciones y las
clasificaciones registradas aplicables.
"""

from __future__ import annotations

import ipaddress
from typing import TypedDict

from netops_desk.exceptions import DomainError


__all__ = [
    "DomainError",
    "ErrorCode",
    "IPv6Result",
    "calculate",
]


class ErrorCode:
    """Códigos de error estables del contrato de la API IPv6.

    Viajan al cliente en el campo 'error' de la respuesta. No deben
    cambiarse sin actualizar el contrato y los clientes consumidores.
    """

    INVALID_CIDR = "invalid_cidr"
    INVALID_PREFIX = "invalid_prefix"
    ZONE_ID_NOT_SUPPORTED = "zone_id_not_supported"


class DomainWarning(TypedDict):
    """Advertencia con código estable y mensaje legible."""

    code: str
    message: str


class IPv6Result(TypedDict):
    """Resultado del cálculo IPv6 para un CIDR."""

    input: str
    address: str
    prefix_length: int
    network: str
    last_address: str
    total_addresses: str
    host_bits_set: bool
    classifications: list[str]
    warnings: list[DomainWarning]


def _error(code: str, message: str) -> DomainError:
    """Crea un error de dominio con el código y el mensaje indicados."""
    return DomainError(message=message, code=code)


def _warning(code: str, message: str) -> DomainWarning:
    """Construye una advertencia con un código y un mensaje."""
    return {"code": code, "message": message}


def _validate_cidr(cidr: object) -> tuple[ipaddress.IPv6Address, int]:
    """Valida y convierte un CIDR IPv6 en dirección y prefijo.

    Acepta exclusivamente el formato 'direccion/prefijo'. Rechaza zone
    IDs (por ejemplo, 'fe80::1%eth0/64') según D3.

    Lanza DomainError con:
    - INVALID_CIDR: tipo incorrecto, estructura incorrecta o dirección
      IPv6 no parseable.
    - INVALID_PREFIX: prefijo no entero, vacío o fuera de 0..128.
    - ZONE_ID_NOT_SUPPORTED: la entrada contiene un identificador '%'.
    """
    # 1. Debe ser una cadena.
    if not isinstance(cidr, str):
        raise _error(
            ErrorCode.INVALID_CIDR,
            "El campo 'cidr' debe ser una cadena.",
        )

    # 2. D3: rechazar zone IDs antes de cualquier otro análisis.
    if "%" in cidr:
        raise _error(
            ErrorCode.ZONE_ID_NOT_SUPPORTED,
            "Los identificadores de zona (por ejemplo, 'fe80::1%eth0') "
            "no están admitidos.",
        )

    # 3. Debe existir exactamente una barra.
    if cidr.count("/") != 1:
        raise _error(
            ErrorCode.INVALID_CIDR,
            "El campo 'cidr' debe contener una dirección IPv6 y un prefijo "
            "separados por '/'.",
        )

    addr_text, _, prefix_text = cidr.partition("/")

    # 4. El prefijo debe ser un entero decimal entre 0 y 128.
    if not prefix_text.isdigit():
        raise _error(
            ErrorCode.INVALID_PREFIX,
            "El prefijo debe ser un entero entre 0 y 128.",
        )

    prefix = int(prefix_text)
    if prefix > 128:
        raise _error(
            ErrorCode.INVALID_PREFIX,
            "El prefijo debe estar entre 0 y 128.",
        )

    # 5. La dirección debe ser un IPv6 válido.
    try:
        address = ipaddress.IPv6Address(addr_text)
    except ipaddress.AddressValueError as exc:
        raise _error(
            ErrorCode.INVALID_CIDR,
            "El campo 'cidr' debe contener una dirección IPv6 válida.",
        ) from exc

    return address, prefix


def calculate(*, cidr: object = None) -> IPv6Result:
    """Calcula la información de una red IPv6 a partir de un CIDR.

    Formato de entrada: 'direccion/prefijo' (por ejemplo, '2001:db8::/64').
    La dirección se canonicaliza a la forma de RFC 5952 en la respuesta.
    Si la dirección contenía bits de host activos, se normaliza a la
    dirección de red y se agrega el warning 'host_bits_normalized'.
    """
    address, prefix = _validate_cidr(cidr)

    # strict=False normaliza bits de host a la dirección de red.
    network = ipaddress.IPv6Network((address, prefix), strict=False)

    host_bits_set = address != network.network_address

    warnings: list[DomainWarning] = []
    if host_bits_set:
        warnings.append(
            _warning(
                "host_bits_normalized",
                "La dirección contenía bits de host; "
                "se calculó la dirección de red.",
            )
        )

    # total_addresses como string decimal: 2^128 > Number.MAX_SAFE_INTEGER.
    total = 1 << (128 - prefix)

    result: IPv6Result = {
        "input": cidr if isinstance(cidr, str) else str(cidr),
        "address": str(address),
        "prefix_length": prefix,
        "network": str(network.network_address),
        "last_address": str(network.broadcast_address),
        "total_addresses": str(total),
        "host_bits_set": host_bits_set,
        "classifications": [],  # se completa en un commit posterior
        "warnings": warnings,
    }

    return result