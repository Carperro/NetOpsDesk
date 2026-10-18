from netops_desk.exceptions import DomainError
import ipaddress
import math


def _usable_host_count(prefixlen: int) -> int:
    """Calcula hosts utilizables para un prefijo, considerando casos borde /31 y /32."""
    if prefixlen == 32:
        return 1
    if prefixlen == 31:
        return 2
    return (2 ** (32 - prefixlen)) - 2


# Modo A: Subnetting por cantidad de subredes. Se calcula el nuevo prefijo y se generan las subredes.

def calculate_subnets_by_count(network_cidr: str, subnet_count: int) -> dict:
    # 1. Validar que la red base sea correcta (strict=False normaliza IPs de host)
    try:
        base_network = ipaddress.ip_network(network_cidr, strict=False)
    except ValueError:
        raise DomainError(
            "Formato de red inválido. Ingresá una dirección IPv4 y un prefijo CIDR válidos."
        ) from None

    # Detectar si hubo normalización (para avisar en el frontend)
    original_ip = network_cidr.split('/')[0]
    was_normalized = original_ip != str(base_network.network_address)

    if subnet_count < 1:
        raise DomainError("La cantidad de subredes debe ser mayor a 0.")

    bits_needed = math.ceil(math.log2(subnet_count))
    new_prefix = base_network.prefixlen + bits_needed

    # Validar capacidad
    max_bits_for_subnets = 32 - base_network.prefixlen
    if bits_needed > max_bits_for_subnets:
        max_subnets = 2 ** max_bits_for_subnets
        raise DomainError(
            f"La red {base_network} solo permite un máximo de {max_subnets} subredes. "
            f"Pediste {subnet_count}."
        )

    subnets = list(base_network.subnets(new_prefix=new_prefix))
    
    # Recortamos la lista por si pidieron un número que no es potencia de 2 (ej: 3 subredes)
    final_subnets = subnets[:subnet_count]
    
    return {
        "subnets": final_subnets,
        "was_normalized": was_normalized,
        "original_network": str(base_network)
    }


# Modo B: Subnetting por cantidad de hosts. Se calcula el nuevo prefijo y se generan las subredes.

def calculate_subnets_by_hosts(network_cidr: str, required_hosts: int) -> dict:
    """
    Divide una red en subredes que puedan contener al menos la cantidad de hosts requeridos.
    """
    # 1. Validar red base (normalizamos si es necesario)
    try:
        base_network = ipaddress.ip_network(network_cidr, strict=False)
    except ValueError:
        raise DomainError(
            "Formato de red inválido. Ingresá una dirección IPv4 y un prefijo CIDR válidos."
        ) from None

    original_ip = network_cidr.split('/')[0]
    was_normalized = original_ip != str(base_network.network_address)

    if required_hosts < 1:
        raise DomainError("La cantidad de hosts requeridos debe ser mayor a 0.")

    # 2. Calcular cuántos bits (h) necesitamos para los hosts
    # La fórmula es 2^h - 2 >= required_hosts.
    # Despejando h usando logaritmos: h >= log2(required_hosts + 2)
    # Usamos math.ceil para redondear hacia arriba (siempre para arriba)
    # Caso borde /31 (RFC 3021): con h=1 se obtienen 2 hosts usables, suficiente para 1 host.
    hosts_needed_with_overhead = required_hosts + 2
    if required_hosts == 1:
        bits_for_hosts = 1
    else:
        bits_for_hosts = math.ceil(math.log2(hosts_needed_with_overhead))

    # 3. Calcular el nuevo prefijo
    new_prefix = 32 - bits_for_hosts

    # 4. Validar que el nuevo prefijo no sea menor al original
    # (No podés pedir subredes más grandes que la red original)
    if new_prefix < base_network.prefixlen:
        max_hosts_possible = _usable_host_count(base_network.prefixlen)
        raise DomainError(
            f"La red original es demasiado pequeña. El máximo de hosts para "
            f"{network_cidr} es {max_hosts_possible}. Pediste {required_hosts}."
        )

    # 5. Generar las subredes
    subnets = list(base_network.subnets(new_prefix=new_prefix))

    # Opcional: Calcular cuántos hosts utilizables tiene cada subred generada
    usable_hosts_per_subnet = _usable_host_count(32 - bits_for_hosts)

    return {
        "subnets": subnets,
        "was_normalized": was_normalized,
        "original_network": str(base_network),
        "new_prefix": new_prefix,
        "usable_hosts_per_subnet": usable_hosts_per_subnet
    }
