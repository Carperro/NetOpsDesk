import pytest
from netops_desk.subnetting import calculate_subnets_by_count,calculate_subnets_by_hosts


# Tests para el modo A de Subnetting: por cantidad de subredes. 
def test_subnetting_happy_path():
    """Caso normal: Red /24 pidiendo 4 subredes (potencia de 2)."""
    result = calculate_subnets_by_count("192.168.1.0/24", 4)
    
    assert result["was_normalized"] is False
    assert len(result["subnets"]) == 4
    
    # Comprobamos que el prefijo resultante sea /26 y la primera red sea la .0
    assert result["subnets"][0].prefixlen == 26
    assert str(result["subnets"][0].network_address) == "192.168.1.0"
    # La última subred debería empezar en .192
    assert str(result["subnets"][3].network_address) == "192.168.1.192"

def test_subnetting_not_power_of_two():
    """Caso límite: Red /24 pidiendo 3 subredes (no es potencia de 2)."""
    result = calculate_subnets_by_count("192.168.1.0/24", 3)
    
    # Aunque pidió 3, internamente calculamos 4 bits (2^2), pero devolvemos solo 3
    assert len(result["subnets"]) == 3
    assert result["subnets"][0].prefixlen == 26

def test_subnetting_normalization():
    """Caso de UX: El usuario ingresa una IP de host en vez de la red."""
    # 192.168.1.5 no es una dirección de red, debería normalizarse a .0
    result = calculate_subnets_by_count("192.168.1.5/24", 4)
    
    assert result["was_normalized"] is True
    assert result["original_network"] == "192.168.1.0/24"

def test_subnetting_insufficient_capacity():
    """Caso de error: Pedir más subredes de las que la red permite."""
    # Una /24 no puede tener 500 subredes
    with pytest.raises(ValueError) as exc_info:
        calculate_subnets_by_count("192.168.1.0/24", 500)
    
    # Verificamos que el mensaje de error sea claro
    assert "solo permite un máximo de 256 subredes" in str(exc_info.value)

def test_subnetting_invalid_network():
    """Caso de error: Formato de red totalmente inválido."""
    with pytest.raises(ValueError):
        calculate_subnets_by_count("esto-no-es-una-ip/24", 4)


# Tests para el modo B de Subnetting: por cantidad de hosts.

def test_subnetting_by_hosts_happy_path():
    """Caso normal: Red /24 pidiendo 50 hosts por subred."""
    result = calculate_subnets_by_hosts("192.168.1.0/24", 50)

    assert result["was_normalized"] is False
    assert result["new_prefix"] == 26
    assert result["usable_hosts_per_subnet"] == 62 # 2^6 - 2
    assert len(result["subnets"]) == 4 # 4 subredes de 64 IPs (256 / 64)
    assert str(result["subnets"][0].network_address) == "192.168.1.0"

def test_subnetting_by_hosts_max_capacity():
    """Caso límite: Red /30 (solo tiene 2 hosts usables) pidiendo 2 hosts."""
    # Una /30 tiene 4 IPs totales. Red, 2 hosts, Broadcast.
    result = calculate_subnets_by_hosts("192.168.1.0/30", 2)
    
    assert result["new_prefix"] == 30
    assert result["usable_hosts_per_subnet"] == 2
    assert len(result["subnets"]) == 1 # No se puede dividir más

def test_subnetting_by_hosts_insufficient_capacity():
    """Caso de error: Pedir 100 hosts a una red /24 (máximo 254 hosts)."""
    # 100 hosts entran en una /24, pero no se puede dividir en subredes más chicas.
    # Si la red original es /24, el prefijo máximo es /32. 
    # Si pide 100 hosts (necesita /25 o /26), la red original /24 sí puede.
    # El error ocurre si pide más hosts de los que la red original tiene.
    with pytest.raises(ValueError) as exc_info:
        calculate_subnets_by_hosts("192.168.1.0/28", 100) # Una /28 tiene 14 hosts usables
    
    assert "El máximo de hosts para" in str(exc_info.value)

def test_subnetting_by_hosts_normalization():
    """Caso de UX: IP de host en vez de red."""
    result = calculate_subnets_by_hosts("10.0.0.5/16", 500)
    
    assert result["was_normalized"] is True
    assert result["original_network"] == "10.0.0.0/16"
    assert result["new_prefix"] == 23 # 500 hosts requieren 512 IPs -> 2^9. 32-9 = 23

def test_subnetting_by_hosts_slash_32_capacity():
    """Caso borde: Red /32 tiene solo 1 host usable; pedir 2 debe fallar con mensaje correcto."""
    with pytest.raises(ValueError) as exc_info:
        calculate_subnets_by_hosts("192.222.1.0/32", 2)
    
    assert "El máximo de hosts para 192.222.1.0/32 es 1" in str(exc_info.value)

def test_subnetting_by_hosts_slash_31_one_host():
    """Caso borde: Red /31 tiene 2 hosts usables (RFC 3021); pedir 1 host debe tener éxito."""
    result = calculate_subnets_by_hosts("192.222.1.0/31", 1)
    
    assert result["usable_hosts_per_subnet"] == 2