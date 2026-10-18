import ipaddress

import pytest
from netops_desk.vlsm import calculate_vlsm
from netops_desk.exceptions import DomainError


def test_vlsm_happy_path():
    """Caso normal: 3 departamentos que entran perfecto en una /24."""
    requerimientos = [
        {"name": "Ventas", "hosts": 100},
        {"name": "IT", "hosts": 50},
        {"name": "Enlace WAN", "hosts": 2}
    ]
    
    result = calculate_vlsm("192.168.1.0/24", requerimientos)
    
    assert len(result["allocated"]) == 3
    
    # Validamos que el orden sea el correcto (Ventas > IT > WAN)
    ventas = result["allocated"][0]
    assert ventas["name"] == "Ventas"
    assert ventas["network"] == "192.168.1.0"
    assert ventas["prefix"] == 25
    
    it = result["allocated"][1]
    assert it["name"] == "IT"
    assert it["network"] == "192.168.1.128"
    assert it["prefix"] == 26
    
    wan = result["allocated"][2]
    assert wan["name"] == "Enlace WAN"
    assert wan["network"] == "192.168.1.192"
    assert wan["prefix"] == 30
    
    # Validamos que el espacio sobrante exista y empiece en .196
    assert len(result["remaining"]) == 1
    assert result["remaining"][0]["network"] == "192.168.1.196"

def test_vlsm_ordenamiento_automatico():
    """Caso crítico: El usuario ingresa los datos desordenados, el sistema debe ordenarlos."""
    # El más chico primero, el más grande al final
    requerimientos = [
        {"name": "WAN", "hosts": 2},
        {"name": "Ventas", "hosts": 100},
        {"name": "IT", "hosts": 50}
    ]
    
    result = calculate_vlsm("10.0.0.0/24", requerimientos)
    
    # Aunque los ingresó desordenados, la salida debe estar de mayor a menor
    assert result["allocated"][0]["name"] == "Ventas"
    assert result["allocated"][1]["name"] == "IT"
    assert result["allocated"][2]["name"] == "WAN"

def test_vlsm_red_muy_chica():
    """Caso de error: Un departamento pide más hosts de los que la red base soporta."""
    requerimientos = [
        {"name": "Fábrica", "hosts": 500} # Una /24 tiene máximo 254 hosts
    ]
    
    with pytest.raises(DomainError) as exc_info:
        calculate_vlsm("192.168.1.0/24", requerimientos)
    
    assert "demasiado grande" in str(exc_info.value)
    assert exc_info.value.code == "insufficient_space"

def test_vlsm_sin_espacio():
    """Caso de error: Los departamentos entran por separado, pero juntos no caben en la red."""
    # La /24 tiene 256 IPs. Si pedimos dos redes que necesitan 128 cada una (total 256) 
    # y sumamos la de 2, ya no entra.
    requerimientos = [
        {"name": "Dep A", "hosts": 100}, # Pide /25 (128 IPs)
        {"name": "Dep B", "hosts": 100}, # Pide /25 (128 IPs)
        {"name": "Dep C", "hosts": 2}    # Pide /30 (4 IPs) -> ¡No hay más espacio!
    ]
    
    with pytest.raises(DomainError) as exc_info:
        calculate_vlsm("192.168.1.0/24", requerimientos)
    
    assert "No hay espacio suficiente" in str(exc_info.value)
    assert exc_info.value.code == "insufficient_space"

def test_vlsm_lista_vacia():
    """Caso de error: No se enviaron requerimientos."""
    with pytest.raises(DomainError) as exc_info:
        calculate_vlsm("192.168.1.0/24", [])

    assert exc_info.value.code == "empty_requirements"


def test_vlsm_limite_exacto():
    result = calculate_vlsm(
        "192.168.1.0/24",
        [{"name": "Ventas", "hosts": 254}],
    )

    assert len(result["allocated"]) == 1
    assert result["allocated"][0]["prefix"] == 24
    assert result["allocated"][0]["hosts_needed"] == 254
    assert result["remaining"] == []


def test_vlsm_red_slash_30():
    result = calculate_vlsm(
        "192.168.1.0/30",
        [{"name": "Enlace", "hosts": 2}],
    )

    assert len(result["allocated"]) == 1
    assert result["allocated"][0]["network"] == "192.168.1.0"
    assert result["allocated"][0]["prefix"] == 30
    assert result["allocated"][0]["hosts_needed"] == 2
    assert result["remaining"] == []


def test_vlsm_espacio_exacto():
    result = calculate_vlsm(
        "192.168.1.0/24",
        [
            {"name": "Ventas", "hosts": 126},
            {"name": "IT", "hosts": 126},
        ],
    )

    assert [subnet["prefix"] for subnet in result["allocated"]] == [25, 25]
    assert result["remaining"] == []


def test_vlsm_nombres_duplicados():
    result = calculate_vlsm(
        "192.168.1.0/24",
        [
            {"name": "Ventas", "hosts": 50},
            {"name": "Ventas", "hosts": 20},
        ],
    )

    assert len(result["allocated"]) == 2
    assert [subnet["name"] for subnet in result["allocated"]] == ["Ventas", "Ventas"]


def test_vlsm_ipv6_rechazado():
    with pytest.raises(DomainError) as exc_info:
        calculate_vlsm("2001:db8::/32", [{"name": "Ventas", "hosts": 10}])

    assert str(exc_info.value) == "VLSM solo está soportado para IPv4."
    assert exc_info.value.code == "invalid_network"


def test_vlsm_normaliza_la_red_base_y_conserva_los_requerimientos():
    requirements = [
        {"name": "Sucursal", "hosts": 10},
        {"name": "Central", "hosts": 100},
    ]
    original_requirements = [item.copy() for item in requirements]

    result = calculate_vlsm("192.168.1.99/24", requirements)

    assert result["base_network"] == "192.168.1.0/24"
    assert [item["name"] for item in result["allocated"]] == ["Central", "Sucursal"]
    assert requirements == original_requirements


def test_vlsm_asignaciones_no_se_solapan_y_quedan_dentro_de_la_red_base():
    result = calculate_vlsm(
        "10.20.0.0/22",
        [
            {"name": "A", "hosts": 200},
            {"name": "B", "hosts": 80},
            {"name": "C", "hosts": 20},
            {"name": "D", "hosts": 2},
        ],
    )

    allocated = result["allocated"]
    assert [item["hosts_needed"] for item in allocated] == [200, 80, 20, 2]
    for current, following in zip(allocated, allocated[1:]):
        current_end = int(ipaddress.IPv4Address(current["broadcast"]))
        following_start = int(ipaddress.IPv4Address(following["network"]))
        assert current_end < following_start
    base = ipaddress.ip_network(result["base_network"])
    assert all(ipaddress.ip_network(item["network"]).subnet_of(base) for item in allocated)


def test_vlsm_rechaza_cidr_malformado():
    with pytest.raises(DomainError, match="Formato de red inválido") as exc_info:
        calculate_vlsm("no-es-un-cidr", [{"name": "Ventas", "hosts": 10}])

    assert exc_info.value.code == "invalid_network"


@pytest.mark.parametrize(
    "requirement",
    [
        {"name": "Ventas", "hosts": 0},
        {"name": "   ", "hosts": 10},
    ],
)
def test_vlsm_rechaza_requerimientos_invalidos_con_codigo(requirement):
    with pytest.raises(DomainError) as exc_info:
        calculate_vlsm("192.168.1.0/24", [requirement])

    assert exc_info.value.code == "invalid_requirement"


def test_vlsm_rechaza_limite_de_requerimientos_mas_uno():
    requirements = [
        {"name": f"Red {index}", "hosts": 1}
        for index in range(101)
    ]

    with pytest.raises(DomainError) as exc_info:
        calculate_vlsm("192.168.1.0/24", requirements)

    assert exc_info.value.code == "invalid_requirement"
    assert "más de 100" in str(exc_info.value)


def test_vlsm_el_espacio_restante_es_contiguo_y_su_cantidad_inclusiva():
    result = calculate_vlsm(
        "192.0.2.0/29",
        [{"name": "LAN", "hosts": 2}],
    )

    assert result["remaining"] == [
        {"network": "192.0.2.4", "broadcast": "192.0.2.7", "total_ips": 4}
    ]


def test_vlsm_nombres_con_caracteres_especiales_se_conservan_como_datos():
    result = calculate_vlsm(
        "192.0.2.0/24",
        [{"name": '<img src=x onerror="alert(1)">', "hosts": 10}],
    )

    assert result["allocated"][0]["name"] == '<img src=x onerror="alert(1)">'
