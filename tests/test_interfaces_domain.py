import pytest
from netops_desk.exceptions import DomainError
from netops_desk.interfaces import ErrorCode, execute_interfaces, InterfaceInfo

class FakeRunner:
    def __init__(self, raises: bool = False):
        self.raises = raises
    def run(self) -> list[InterfaceInfo]:
        if self.raises: raise Exception("Error")
        return [{"name": "Ethernet", "mac_address": "AA", "ipv4": "1.1.1.1", "netmask": "255", "gateway": "1.1.1.1", "dns_servers": [], "is_up": True, "speed_mbps": 1000}]

def test_interfaces_exitoso():
    res = execute_interfaces(runner=FakeRunner())
    assert len(res["interfaces"]) == 1
    assert res["interfaces"][0]["name"] == "Ethernet"

def test_interfaces_error_sistema():
    with pytest.raises(DomainError) as exc:
        execute_interfaces(runner=FakeRunner(raises=True))
    assert exc.value.code == ErrorCode.EXECUTION_FAILED