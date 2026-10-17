"""Cálculos puros del dominio IPv4/CIDR para NetOps Desk.

Este módulo contiene la lógica de negocio pura del cálculo de redes IPv4.
No depende de FastAPI, Pydantic, HTTP ni de ninguna otra capa de
infraestructura. Solo utiliza la biblioteca estándar de Python (ipaddress).

Los códigos de error (ErrorCode) forman parte del contrato de la API y no
deben cambiarse sin actualizar el contrato. Los mensajes de error sí pueden
cambiar libremente.
"""

from __future__ import annotations

import ipaddress
from typing import TypedDict

from netops_desk.exceptions import DomainError


__all__ = [
    "DomainError",
    "ErrorCode",
    "IPv4DirectResult",
    "IPv4InverseResult",
    "MODES",
    "calculate_direct",
    "calculate_inverse",
]


# Modos de cálculo permitidos por el contrato.
MODES = ("conventional", "point-to-point")


class ErrorCode:
    """Códigos de error estables del contrato de la API.

    Viajan al cliente en el campo 'error' de la respuesta. No deben
    cambiarse sin actualizar el contrato y los clientes consumidores.
    """

    INVALID_TYPE = "invalid_type"
    INVALID_VALUE = "invalid_value"
    MISSING_FIELD = "missing_field"
    INCOMPATIBLE_INPUTS = "incompatible_inputs"
    NON_CONTIGUOUS_NETMASK = "non_contiguous_netmask"
    INSUFFICIENT_CAPACITY = "insufficient_capacity"


class DomainWarning(TypedDict):
    """Advertencia con código estable y mensaje legible."""

    code: str
    message: str


class BinaryRepresentation(TypedDict):
    """Representación binaria de los campos de una red IPv4."""

    network: str | None
    broadcast: str | None
    netmask: str | None
    wildcard: str | None
    first_usable: str | None
    last_usable: str | None


class IPv4DirectResult(TypedDict):
    """Resultado del cálculo directo (CIDR o address+netmask)."""

    network: str
    broadcast: str | None
    netmask: str
    wildcard: str
    first_usable: str | None
    last_usable: str | None
    total_addresses: int
    usable_addresses: int
    warnings: list[DomainWarning]
    binary: BinaryRepresentation


class IPv4InverseResult(TypedDict):
    """Resultado del cálculo inverso (hosts requeridos)."""

    required_hosts: int
    mode_requested: str
    mode_applied: str
    prefix: int
    total_addresses: int
    usable_addresses: int
    warnings: list[DomainWarning]


def _error(code: str, message: str) -> DomainError:
    """Crea un error de dominio con el código y el mensaje indicados."""
    return DomainError(message=message, code=code)


def _validate_mode(mode: object) -> str:
    """Valida el modo solicitado y lo devuelve como cadena."""
    if not isinstance(mode, str) or mode not in MODES:
        raise _error(
            ErrorCode.INVALID_VALUE,
            "El modo debe ser 'conventional' o 'point-to-point'.",
        )
    return mode


def _parse_ipv4(value: object, field: str) -> ipaddress.IPv4Address:
    """Valida y convierte un valor en una dirección IPv4.

    Acepta tanto cadenas (ej: '192.168.1.1') como objetos IPv4Address ya
    parseados, porque la capa de API puede entregar cualquiera de los dos
    según cómo los valide Pydantic.
    """
    # Si ya es un objeto IPv4Address, lo devolvemos tal cual.
    if isinstance(value, ipaddress.IPv4Address):
        return value

    # Si no es cadena, es un error de tipo.
    if not isinstance(value, str):
        raise _error(
            ErrorCode.INVALID_TYPE,
            f"El campo '{field}' debe ser una cadena IPv4.",
        )

    try:
        return ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError as exc:
        raise _error(
            ErrorCode.INVALID_VALUE,
            f"El campo '{field}' debe ser una dirección IPv4 válida.",
        ) from exc

def _as_ipv4(value: int | ipaddress.IPv4Address) -> str:
    """Convierte un entero o un objeto IPv4 en texto decimal con puntos."""
    return str(ipaddress.IPv4Address(value))


def _binary(value: str | None) -> str | None:
    """Convierte una IPv4 a cuatro grupos binarios de ocho bits."""
    # Si el campo original no tiene valor, su representación binaria
    # tampoco debe tenerlo.
    if value is None:
        return None

    # Separamos los cuatro octetos de la dirección.
    octets = value.split(".")

    # Convertimos cada octeto a binario y completamos con ceros a la
    # izquierda hasta alcanzar ocho bits.
    return ".".join(f"{int(octet):08b}" for octet in octets)


def _warning(code: str, message: str) -> DomainWarning:
    """Construye una advertencia con un código y un mensaje."""
    return {"code": code, "message": message}


def calculate_direct(
    *,
    cidr: object = None,
    address: object = None,
    netmask: object = None,
    mode: object = "conventional",
) -> IPv4DirectResult:
    """Calcula la información de una red IPv4 a partir de su entrada.

    Acepta dos formas mutuamente excluyentes:
    - 'cidr': dirección IPv4 con prefijo (ej: '192.168.1.0/24').
    - 'address' + 'netmask': dirección IPv4 y máscara de subred.
    """
    selected_mode = _validate_mode(mode)

    # Detectamos qué forma de entrada se recibió.
    # Las formas admitidas son CIDR o dirección más máscara.
    has_cidr = cidr is not None
    has_address = address is not None
    has_netmask = netmask is not None

    # No permitimos combinar ambas formas de entrada.
    if has_cidr and (has_address or has_netmask):
        raise _error(
            ErrorCode.INCOMPATIBLE_INPUTS,
            "Los campos 'cidr' y 'address'/'netmask' son mutuamente excluyentes.",
        )

    if has_cidr:
        # CIDR debe recibirse como texto, por ejemplo "192.0.2.1/24".
        if not isinstance(cidr, str):
            raise _error(
                ErrorCode.INVALID_TYPE,
                "El campo 'cidr' debe ser una cadena.",
            )

        # Debe existir exactamente una barra para separar dirección y prefijo.
        if cidr.count("/") != 1:
            raise _error(
                ErrorCode.INVALID_VALUE,
                "El campo 'cidr' debe contener una dirección IPv4 y un "
                "prefijo separados por '/'.",
            )

        try:
            # strict=False permite normalizar una dirección que tenga bits
            # de host activos a la dirección de red correspondiente.
            network = ipaddress.IPv4Network(cidr, strict=False)
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError) as exc:
            raise _error(
                ErrorCode.INVALID_VALUE,
                "El campo 'cidr' debe contener una dirección IPv4 y un "
                "prefijo válidos.",
            ) from exc

        # Conservamos la dirección recibida para detectar si fue necesario
        # normalizarla después de calcular la red.
        input_address = _parse_ipv4(cidr.partition("/")[0], "cidr address")

    else:
        # Si se elige la forma alternativa, deben llegar ambos campos.
        if has_address != has_netmask:
            raise _error(
                ErrorCode.MISSING_FIELD,
                "Los campos 'address' y 'netmask' deben proporcionarse juntos.",
            )

        if not has_address:
            raise _error(
                ErrorCode.MISSING_FIELD,
                "Se requiere 'cidr' o los campos 'address' y 'netmask'.",
            )

        input_address = _parse_ipv4(address, "address")
        mask_address = _parse_ipv4(netmask, "netmask")

        # Convertimos la máscara en una cadena de 32 bits.
        mask_bits = f"{int(mask_address):032b}"

        # En una máscara válida, todos los bits de red (1) preceden a los
        # bits de host (0). El número de unos determina el prefijo.
        prefix = mask_bits.count("1")

        # Comparamos la máscara completa con el patrón esperado.
        # Esto detecta máscaras no contiguas, como 255.0.255.0.
        if mask_bits != ("1" * prefix + "0" * (32 - prefix)):
            raise _error(
                ErrorCode.NON_CONTIGUOUS_NETMASK,
                "La máscara de red debe ser contigua.",
            )

        # Construimos la red utilizando la dirección y el prefijo calculado.
        # strict=False normaliza cualquier bit de host activo.
        network = ipaddress.IPv4Network((input_address, prefix), strict=False)

    # A partir de aquí ya tenemos una red IPv4 válida.
    prefix = network.prefixlen
    total = network.num_addresses
    warnings: list[DomainWarning] = []

    # Si la dirección recibida no coincide con la dirección de red, se
    # modificó su parte de host al normalizarla.
    if input_address != network.network_address:
        warnings.append(
            _warning(
                "host_bits_normalized",
                "La dirección contenía bits de host; se calculó la dirección de red.",
            )
        )

    # El modo point-to-point tiene un tratamiento especial únicamente para
    # los prefijos /31 y /32.
    point_to_point = selected_mode == "point-to-point" and prefix in (31, 32)

    # Para los demás prefijos se aplica el comportamiento convencional y se
    # informa que point-to-point no resulta aplicable.
    if selected_mode == "point-to-point" and not point_to_point:
        warnings.append(
            _warning(
                "point_to_point_not_applicable",
                "Point-to-point no aplica al prefijo seleccionado; se aplicó conventional.",
            )
        )

    # La máscara de red y la wildcard son complementarias: los bits 1 de una
    # corresponden a bits 0 de la otra.
    mask = network.netmask
    wildcard = ipaddress.IPv4Address(int(mask) ^ 0xFFFFFFFF)

    # Estos campos pueden ser None, dependiendo del prefijo y del modo.
    broadcast: str | None
    first_usable: str | None
    last_usable: str | None

    if prefix >= 31 and not point_to_point:
        # En modo convencional, /31 y /32 tienen cero direcciones utilizables
        # según las reglas de este proyecto.
        usable = 0
        broadcast = first_usable = last_usable = None

    elif point_to_point:
        # En point-to-point, todas las direcciones del bloque son utilizables
        # para /31 y /32. No se asigna una dirección de broadcast dedicada.
        usable = total
        broadcast = None
        first_usable = _as_ipv4(network.network_address)
        last_usable = _as_ipv4(network.broadcast_address)

    else:
        # En los prefijos convencionales hasta /30, se reservan dos
        # direcciones: la dirección de red y la dirección de broadcast.
        usable = total - 2
        broadcast = _as_ipv4(network.broadcast_address)
        first_usable = _as_ipv4(int(network.network_address) + 1)
        last_usable = _as_ipv4(int(network.broadcast_address) - 1)

    # Construimos la respuesta pública del cálculo directo.
    # Los nombres de las claves deben coincidir con el contrato de la API.
    result: IPv4DirectResult = {
        "network": _as_ipv4(network.network_address),
        "broadcast": broadcast,
        "netmask": _as_ipv4(mask),
        "wildcard": _as_ipv4(wildcard),
        "first_usable": first_usable,
        "last_usable": last_usable,
        "total_addresses": total,
        "usable_addresses": usable,
        "warnings": warnings,
        "binary": {
            "network": _binary(_as_ipv4(network.network_address)),
            "broadcast": _binary(broadcast),
            "netmask": _binary(_as_ipv4(mask)),
            "wildcard": _binary(_as_ipv4(wildcard)),
            "first_usable": _binary(first_usable),
            "last_usable": _binary(last_usable),
        },
    }

    return result


def calculate_inverse(
    *,
    required_hosts: object,
    mode: object,
) -> IPv4InverseResult:
    """Busca el prefijo más largo que satisface la cantidad de hosts solicitada."""
    selected_mode = _validate_mode(mode)

    # En Python, bool es una subclase de int. Por eso hay que rechazar
    # True y False expresamente aunque técnicamente sean valores enteros.
    if isinstance(required_hosts, bool) or not isinstance(required_hosts, int):
        raise _error(
            ErrorCode.INVALID_TYPE,
            "El campo 'required_hosts' debe ser un número entero.",
        )

    if required_hosts < 1:
        raise _error(
            ErrorCode.INVALID_VALUE,
            "El campo 'required_hosts' debe ser al menos 1.",
        )

    # Todavía no se conoce un prefijo que satisfaga la solicitud.
    selected_prefix: int | None = None
    selected_total = 0
    selected_usable = 0
    selected_mode_applied = "conventional"

    # Recorremos los prefijos desde /32 hasta /0. El primer prefijo que
    # satisface la capacidad es el más largo posible.
    for prefix in range(32, -1, -1):
        # Cantidad total de direcciones del bloque IPv4.
        # Por ejemplo, /30 contiene 2**2 = 4 direcciones.
        total = 1 << (32 - prefix)

        # Point-to-point es aplicable solo a /31 y /32.
        point_to_point = selected_mode == "point-to-point" and prefix in (31, 32)

        # Calculamos la capacidad utilizable según el modo efectivo.
        usable = total if point_to_point else (0 if prefix >= 31 else total - 2)

        if usable >= required_hosts:
            # Guardamos el primer prefijo capaz de cumplir la solicitud.
            selected_prefix = prefix
            selected_total = total
            selected_usable = usable

            # Registramos el modo realmente aplicado, que puede diferir del
            # solicitado si el prefijo no es /31 ni /32.
            selected_mode_applied = "point-to-point" if point_to_point else "conventional"
            break

    # Si ningún prefijo satisface la solicitud, incluso /0 resulta insuficiente.
    if selected_prefix is None:
        raise _error(
            ErrorCode.INSUFFICIENT_CAPACITY,
            "La cantidad de hosts solicitada supera la capacidad máxima de /0.",
        )

    warnings: list[DomainWarning] = []

    # Si el usuario pidió point-to-point pero el prefijo elegido no es /31
    # ni /32, se aplicó el comportamiento convencional.
    if selected_mode == "point-to-point" and selected_prefix not in (31, 32):
        warnings.append(
            _warning(
                "point_to_point_not_applicable",
                "Point-to-point no aplica al prefijo seleccionado; se aplicó conventional.",
            )
        )

    # El cálculo inverso no recibe una dirección base, por lo que devuelve el
    # prefijo y la capacidad, pero no inventa una dirección de red.
    return {
        "required_hosts": required_hosts,
        "mode_requested": selected_mode,
        "mode_applied": selected_mode_applied,
        "prefix": selected_prefix,
        "total_addresses": selected_total,
        "usable_addresses": selected_usable,
        "warnings": warnings,
    }
