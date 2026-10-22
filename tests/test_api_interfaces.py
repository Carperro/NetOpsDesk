"""Tests de contrato HTTP para Interfaces."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app
from netops_desk.api.routes.interfaces import get_interfaces_runner
from netops_desk.exceptions import DomainError
from netops_desk.interfaces import ErrorCode, InterfaceInfo

ENDPOINT = "/api/v1/tools/interfaces/execute"

class FakeRunner:
    def __init__(self, raises: bool = False):
        self.raises = raises

    def run(self) -> list[InterfaceInfo]:
        if self.raises:
            raise Exception("Fallo del sistema")
        return [{
            "name": "Ethernet", "mac_address": "AA:BB:CC:DD:EE:FF",
            "ipv4": "192.168.1.50", "netmask": "255.255.255.0",
            "gateway": "192.168.1.1", "dns_servers": ["8.8.8.8"],
            "is_up": True, "speed_mbps": 1000
        }]

def test_interfaces_exitoso(client: TestClient):
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert len(data["interfaces"]) == 1
    assert data["interfaces"][0]["gateway"] == "192.168.1.1"
    assert data["interfaces"][0]["dns_servers"] == ["8.8.8.8"]

def test_interfaces_error_sistema(app):
    app.dependency_overrides[get_interfaces_runner] = lambda: FakeRunner(True)
    custom_client = TestClient(app)
    
    response = custom_client.get(ENDPOINT)
    assert response.status_code == 422 
    assert response.json()["error"] == "execution_failed"
