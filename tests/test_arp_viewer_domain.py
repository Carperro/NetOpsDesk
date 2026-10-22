import pytest

import netops_desk.arp_viewer as arp_viewer
from netops_desk.arp_viewer import ArpExecutionResult, ErrorCode, execute_arp_viewer
from netops_desk.exceptions import DomainError


class FakeRunner:
    def __init__(self, exit_code: int = 0):
        self.exit_code = exit_code
    def run(self) -> ArpExecutionResult:
        if self.exit_code != 0:
            return {"exit_code": self.exit_code, "stdout": b"", "stderr": b""}
        output = (
            "Interfaz: 192.168.1.33 --- 0x5\n"
            "  192.168.1.1           aa-bb-cc-dd-ee-ff     dinámico\n"
            "  192.168.1.255         ff-ff-ff-ff-ff-ff     estático\n"
        )
        return {"exit_code": 0, "stdout": output.encode("cp850"), "stderr": b""}

def test_arp_parseo_exitoso():
    res = execute_arp_viewer(runner=FakeRunner())
    assert len(res["entries"]) == 2
    assert res["entries"][0]["entry_type"] == "dynamic"
    assert res["entries"][1]["entry_type"] == "static"
    assert res["entries"][0]["mac_address"] == "aa-bb-cc-dd-ee-ff"

def test_arp_error_comando():
    with pytest.raises(DomainError) as exc:
        execute_arp_viewer(runner=FakeRunner(exit_code=1))
    assert exc.value.code == ErrorCode.EXECUTION_FAILED


def test_arp_decodifica_texto_cp850_con_acentos(monkeypatch):
    decoded = []
    output = "Interfaz: 192.168.1.33 --- 0x5\n  192.168.1.1 aa-bb-cc-dd-ee-ff din\u00e1mico\n"

    class AccentedRunner:
        def run(self) -> ArpExecutionResult:
            return {"exit_code": 0, "stdout": output.encode("cp850"), "stderr": b""}

    monkeypatch.setattr(arp_viewer, "_parse_arp", lambda text: decoded.append(text) or [])
    execute_arp_viewer(runner=AccentedRunner())

    assert decoded == [output]
