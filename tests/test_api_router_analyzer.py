"""Tests de contrato HTTP para el Analizador de Rutas."""

import pytest
from fastapi.testclient import TestClient

from netops_desk.api.main import create_app
from netops_desk.api.routes.route_analyzer import get_route_runner
from netops_desk.exceptions import DomainError
from netops_desk.route_analyzer import ErrorCode, RouteExecutionResult

ENDPOINT = "/api/v1/tools/route-analyzer/execute"

class FakeRunner:
    def __init__(self, exit_code: int = 0):
        self.exit_code = exit_code

    def run(self) -> RouteExecutionResult:
        if self.exit_code != 0:
             return {"ipconfig_stdout": b"", "route_stdout": b"", "exit_code": self.exit_code}
        
        return {
            "ipconfig_stdout": b"Default Gateway . . . : 192.168.1.1",
            "route_stdout": b"0.0.0.0 0.0.0.0 192.168.1.1 192.168.1.50 25",
            "exit_code": 0,
        }


def test_route_analyzer_exitoso(client: TestClient):
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert data["default_gateway"] == "192.168.1.1"
    assert len(data["routes"]) == 1
    assert data["routes"][0]["metric"] == 25

def test_route_analyzer_error_sistema(app):
    app.dependency_overrides[get_route_runner] = lambda: FakeRunner(1)
    custom_client = TestClient(app)
    
    response = custom_client.get(ENDPOINT)
    assert response.status_code == 422 # Mapeado por handler global (execution_failed)
    assert response.json()["error"] == "execution_failed"
