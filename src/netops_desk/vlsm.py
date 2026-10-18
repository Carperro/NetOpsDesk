from __future__ import annotations

import ipaddress
import math

from netops_desk.exceptions import DomainError

MAX_REQUIREMENTS = 100


class ErrorCode:
    """Códigos estables de los errores del dominio VLSM."""

    INVALID_NETWORK = "invalid_network"
    EMPTY_REQUIREMENTS = "empty_requirements"
    INVALID_REQUIREMENT = "invalid_requirement"
    INSUFFICIENT_SPACE = "insufficient_space"


def _error(code: str, message: str) -> DomainError:
    """Crea un error de dominio con código contractual estable."""
    return DomainError(message=message, code=code)


def calculate_vlsm(network_cidr: str, requirements: list[dict]) -> dict:
    """
    Calcula la asignación VLSM para una lista de requerimientos.
    
    Args:
        network_cidr: Red base (ej. "192.168.1.0/24").
        requirements: Lista de dicts, ej: [{"name": "Ventas", "hosts": 100}, ...]
    """
    # 1. Validaciones iniciales
    if not requirements:
        raise _error(
            ErrorCode.EMPTY_REQUIREMENTS,
            "Debés proporcionar al menos un requerimiento.",
        )

    if len(requirements) > MAX_REQUIREMENTS:
        raise _error(
            ErrorCode.INVALID_REQUIREMENT,
            "No se permiten más de 100 requerimientos por solicitud.",
        )
    
    try:
        base_network = ipaddress.ip_network(network_cidr, strict=False)
    except ValueError:
        raise _error(
            ErrorCode.INVALID_NETWORK,
            "Formato de red inválido. Ingresá una dirección IPv4 y un prefijo CIDR válidos."
        ) from None

    if base_network.version != 4:
        raise _error(ErrorCode.INVALID_NETWORK, "VLSM solo está soportado para IPv4.")

    for req in requirements:
        if req["hosts"] <= 0 or not req["name"].strip():
            raise _error(
                ErrorCode.INVALID_REQUIREMENT,
                "Cada requerimiento debe tener un nombre y una cantidad de hosts mayor que 0.",
            )

    # 2. REGLA DE ORO: Ordenar de mayor a menor (los más grandes primero)
    # Usamos una función lambda para ordenar la lista en base a la llave 'hosts'
    sorted_requirements = sorted(requirements, key=lambda x: x["hosts"], reverse=True)

    # 3. Inicializamos el puntero de IP actual
    # ... (todo el código de validación inicial y ordenamiento de la lista) ...

    current_ip = base_network.network_address
    base_broadcast = base_network.broadcast_address
    allocated_subnets = []

    for req in sorted_requirements:
        name = req["name"]
        hosts_needed = req["hosts"]

        # 1. Calcular los bits y el prefijo (ya lo vimos)
        bits_for_hosts = math.ceil(math.log2(hosts_needed + 2))
        new_prefix = 32 - bits_for_hosts

        if new_prefix < base_network.prefixlen:
            raise _error(
                ErrorCode.INSUFFICIENT_SPACE,
                f"El requerimiento '{name}' es demasiado grande para la red base.",
            )

        # 2. CREAR LA SUBRED con la IP actual y el nuevo prefijo
        # f"{current_ip}/{new_prefix}" se convierte en string, ej: "192.168.1.0/25"
        subnet = ipaddress.ip_network(f"{current_ip}/{new_prefix}", strict=False)

        # 3. VERIFICAR SI NOS PASAMOS DEL LÍMITE DEL TERRENO
        # Comparamos el broadcast de esta subred con el broadcast de la red base original
        if subnet.broadcast_address > base_broadcast:
            raise _error(
                ErrorCode.INSUFFICIENT_SPACE,
                f"No hay espacio suficiente para el requerimiento '{name}'.",
            )

        # 4. GUARDAR LA SUBRED ASIGNADA
        allocated_subnets.append({
            "name": name,
            "network": str(subnet.network_address),
            "prefix": subnet.prefixlen,
            "netmask": str(subnet.netmask),
            "broadcast": str(subnet.broadcast_address),
            "first_host": str(subnet.network_address + 1),
            "last_host": str(subnet.broadcast_address - 1),
            "total_ips": subnet.num_addresses,
            "hosts_needed": hosts_needed
        })

        # 5. AVANZAR EL PUNTERO AL SIGUIENTE HUECO LIBRE
        # La siguiente IP disponible es el broadcast actual + 1
        current_ip = subnet.broadcast_address + 1

    # 6. CALCULAR EL ESPACIO SOBRANTE (Opcional, pero muy útil para el frontend)

    remaining_ips = []
    if current_ip <= base_broadcast:
        # Calculamos la diferencia entre la última IP y la primera libre
        total_remaining = int(base_broadcast) - int(current_ip) + 1
        remaining_ips.append({
            "network": str(current_ip),
            "broadcast": str(base_broadcast),
            "total_ips": total_remaining
        })

    return {
        "base_network": str(base_network),
        "allocated": allocated_subnets,
        "remaining": remaining_ips
    }
