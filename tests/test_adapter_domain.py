import pytest
from netops_desk.exceptions import DomainError
from netops_desk.adapters import ErrorCode, execute_adapters, AdapterInfo

class FakeRunner:
    def __init__(self, raises: bool = False):
        self.raises = raises
    def run(self) -> list[AdapterInfo]:
        if self.raises: raise Exception("Fallo")
        return [{"name": "Wi-Fi", "is_up": True, "speed_mbps": 433, "mtu": 1500, "is_multicast": False}]

def test_adapters_exitoso():
    res = execute_adapters(runner=FakeRunner())
    assert len(res["adapters"]) == 1
    assert res["adapters"][0]["name"] == "Wi-Fi"

def test_adapters_error():
    with pytest.raises(DomainError) as exc:
        execute_adapters(runner=FakeRunner(raises=True))
    assert exc.value.code == ErrorCode.EXECUTION_FAILED