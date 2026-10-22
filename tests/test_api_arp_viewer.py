"""Tests de contrato HTTP para el Visor ARP."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app
from netops_desk.api.routes.arp_viewer import get_arp_runner
from netops_desk.arp_viewer import ArpExecutionResult

ENDPOINT = "/api/v1/tools/arp-viewer/execute"

class FakeArpRunner:
    def __init__(self, exit_code: int = 0):
        self.exit_code = exit_code

    def run(self) -> ArpExecutionResult:
        if self.exit_code != 0:
            return {"exit_code": self.exit_code, "stdout": b"", "stderr": b""}
        output = (
            "Interfaz: 192.168.1.33 --- 0x5\n"
            "  192.168.1.1           aa-bb-cc-dd-ee-ff     dinámico\n"
        )
        return {"exit_code": 0, "stdout": output.encode(), "stderr": b""}

def test_arp_exitoso(client: TestClient):
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert len(data["entries"]) == 1
    assert data["entries"][0]["ip_address"] == "192.168.1.1"
    assert data["entries"][0]["entry_type"] == "dynamic"

def test_arp_error_sistema(app):
    app.dependency_overrides[get_arp_runner] = lambda: FakeArpRunner(1)
    custom_client = TestClient(app)
    
    response = custom_client.get(ENDPOINT)
    assert response.status_code == 422
    assert response.json()["error"] == "execution_failed"
