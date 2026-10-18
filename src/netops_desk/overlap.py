import ipaddress
from itertools import combinations
from netops_desk.exceptions import DomainError

def detect_overlaps(networks: list[str]) -> dict:
    if len(networks) < 2:
        raise DomainError("Se requieren al menos dos redes para detectar solapamientos.")    

    parsed_networks = []

    for net_str in networks:
        try:
            net_obj = ipaddress.ip_network(net_str, strict=False)
            if net_obj.version != 4:
                raise DomainError(f"La red '{net_str}' no es una red IPv4 válida.")
            parsed_networks.append(net_obj)
        except ValueError as e:
            raise DomainError(f"Formato de red inválido en '{net_str}': {str(e)}")

    overlaps = []
    for net_a, net_b in combinations(parsed_networks, 2):
        if net_a.overlaps(net_b):
            if net_a.subnet_of(net_b):
                msg = f"La red {net_a} está completamente dentro de {net_b}."
            elif net_b.subnet_of(net_a):
                msg = f"La red {net_b} está completamente dentro de {net_a}."
            else:
                msg = "Estas redes se solapan parcialmente."
                
            overlaps.append({
                "network_a": str(net_a),
                "network_b": str(net_b),
                "message": msg
            })
            
    return {
        "networks": networks,
        "has_overlap": len(overlaps) > 0,
        "overlaps": overlaps,
    }