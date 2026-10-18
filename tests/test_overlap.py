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

def test_overlap_red_invalida():
    """Caso de error: Formato de red inválido."""
    with pytest.raises(DomainError) as exc_info:
        detect_overlaps(["192.168.1.0/24", "192.168.1.0/abc"])
    
    assert "Formato de red inválido" in str(exc_info.value)