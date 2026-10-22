"""Tests de contrato HTTP para Estado de Adaptadores."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app
from netops_desk.api.routes.adapters import get_adapters_runner
from netops_desk.adapters import AdapterInfo

ENDPOINT = "/api/v1/tools/adapters/execute"

class FakeRunner:
    def run(self) -> list[AdapterInfo]:
        return [{
            "name": "Ethernet",
            "is_up": True,
            "speed_mbps": 1000,
            "mtu": 1500,
            "is_multicast": True
        }]

def test_adapters_exitoso(client: TestClient):
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert len(data["adapters"]) == 1
    assert data["adapters"][0]["name"] == "Ethernet"
    assert data["adapters"][0]["speed_mbps"] == 1000
