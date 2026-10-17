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

def test_vlsm_lista_vacia():
    """Caso de error: No se enviaron requerimientos."""
    with pytest.raises(DomainError):
        calculate_vlsm("192.168.1.0/24", [])


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
