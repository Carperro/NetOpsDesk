import pytest
from netops_desk.exceptions import DomainError
from netops_desk.ip_config import ErrorCode, generate_command

def test_ip_config_renew():
    res = generate_command(action="renew_dhcp", interface_name="Wi-Fi")
    assert 'ipconfig /renew "Wi-Fi"' in res["command"]

def test_ip_config_static():
    res = generate_command(action="set_static", interface_name="Ethernet", ip="192.168.1.100", mask="255.255.255.0", gateway="192.168.1.1")
    assert 'static 192.168.1.100 255.255.255.0 192.168.1.1' in res["command"]

def test_ip_config_error_inyeccion():
    with pytest.raises(DomainError) as exc:
        generate_command(action="renew_dhcp", interface_name='Wi-Fi" & calc.exe')
    assert exc.value.code == ErrorCode.INVALID_INTERFACE_NAME

def test_ip_config_error_faltan_campos():
    with pytest.raises(DomainError) as exc:
        generate_command(action="set_static", interface_name="Wi-Fi", ip="1.1.1.1") # Falta mask y gw
    assert exc.value.code == ErrorCode.MISSING_FIELDS