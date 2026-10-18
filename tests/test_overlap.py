import pytest
from netops_desk.overlap import detect_overlaps
from netops_desk.exceptions import DomainError

def test_overlap_sin_conflictos():
    """Caso feliz: Redes independientes que no se pisan."""
    redes = ["192.168.1.0/24", "10.0.0.0/8", "172.16.0.0/16"]
    result = detect_overlaps(redes)
    
    assert result["has_overlap"] is False
    assert len(result["overlaps"]) == 0 # <-- Cambiado a "overlaps"

def test_overlap_con_conflictos_parciales():
    """Caso crítico: Redes que se solapan parcialmente."""
    redes = ["192.168.1.0/24", "192.168.0.0/23"]
    result = detect_overlaps(redes)
    
    assert result["has_overlap"] is True
    assert len(result["overlaps"]) == 1 # <-- Cambiado a "overlaps"
    assert "se solapan" in result["overlaps"][0]["message"] or "dentro" in result["overlaps"][0]["message"]

def test_overlap_subred_contenida():
    """Caso donde una red está completamente dentro de otra."""
    redes = ["192.168.1.0/24", "192.168.1.64/26"]
    result = detect_overlaps(redes)
    
    assert result["has_overlap"] is True
    assert "está completamente dentro" in result["overlaps"][0]["message"] # <-- Cambiado

def test_overlap_menos_de_dos_redes():
    """Caso de error: El usuario envía menos de 2 redes."""
    with pytest.raises(DomainError) as exc_info:
        detect_overlaps(["192.168.1.0/24"])
    
    assert "al menos dos redes" in str(exc_info.value)
    assert exc_info.value.code == "too_few_networks"

def test_overlap_red_invalida():
    """Caso de error: Formato de red inválido."""
    with pytest.raises(DomainError) as exc_info:
        detect_overlaps(["192.168.1.0/24", "192.168.1.0/abc"])
    
    assert "Formato de red inválido" in str(exc_info.value)
    assert exc_info.value.code == "invalid_network"


def test_overlap_red_ipv6_es_rechazada():
    with pytest.raises(DomainError, match="no es una red IPv4 válida") as exc_info:
        detect_overlaps(["192.0.2.0/24", "2001:db8::/32"])

    assert exc_info.value.code == "invalid_network"


def test_overlap_rechaza_limite_de_redes_mas_uno():
    networks = [f"10.{index}.0.0/16" for index in range(51)]

    with pytest.raises(DomainError) as exc_info:
        detect_overlaps(networks)

    assert exc_info.value.code == "invalid_network"
    assert "más de 50" in str(exc_info.value)


def test_overlap_redes_adyacentes_no_se_solapan():
    result = detect_overlaps(["192.0.2.0/24", "192.0.3.0/24"])

    assert result["has_overlap"] is False
    assert result["overlaps"] == []


@pytest.mark.parametrize(
    ("networks", "expected_message"),
    [
        (["192.0.2.0/24", "192.0.2.0/24"], "completamente dentro"),
        (["192.0.2.0/24", "192.0.2.64/26"], "completamente dentro"),
        (["192.0.2.0/25", "192.0.2.64/26"], "completamente dentro"),
        (["192.0.2.0/23", "192.0.3.0/24"], "completamente dentro"),
    ],
)
def test_overlap_detecta_redes_iguales_o_contenidas(networks, expected_message):
    result = detect_overlaps(networks)

    assert result["has_overlap"] is True
    assert len(result["overlaps"]) == 1
    assert expected_message in result["overlaps"][0]["message"]


def test_overlap_normaliza_hosts_para_comparar_y_conserva_entrada_original():
    networks = ["192.0.2.10/24", "192.0.2.128/25"]

    result = detect_overlaps(networks)

    assert result["networks"] == networks
    assert result["has_overlap"] is True
    assert result["overlaps"][0]["network_a"] == "192.0.2.0/24"
    assert result["overlaps"][0]["network_b"] == "192.0.2.128/25"


def test_overlap_devuelve_todos_los_pares_conflictivos_en_orden_de_entrada():
    result = detect_overlaps(
        ["10.0.0.0/8", "10.1.0.0/16", "10.1.1.0/24", "192.0.2.0/24"]
    )

    assert result["has_overlap"] is True
    assert [
        (item["network_a"], item["network_b"]) for item in result["overlaps"]
    ] == [
        ("10.0.0.0/8", "10.1.0.0/16"),
        ("10.0.0.0/8", "10.1.1.0/24"),
        ("10.1.0.0/16", "10.1.1.0/24"),
    ]
