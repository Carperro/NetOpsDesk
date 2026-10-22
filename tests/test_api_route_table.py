"""Tests de contrato HTTP para la Tabla de Rutas."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app
from netops_desk.api.routes.route_table import get_route_table_runner
from netops_desk.route_table import RouteExecutionResult

ENDPOINT = "/api/v1/tools/route-table/execute"

class FakeRunner:
    def __init__(self, exit_code: int = 0):
        self.exit_code = exit_code

    def run(self) -> RouteExecutionResult:
        if self.exit_code != 0:
            return {"exit_code": self.exit_code, "stdout": b"", "stderr": b""}
        output = (
            "          0.0.0.0          0.0.0.0      192.168.1.1     192.168.1.50     25\n"
            "        127.0.0.0        255.0.0.0         On-link         127.0.0.1    331\n" # Esta se ignora
        )
        return {"exit_code": 0, "stdout": output.encode(), "stderr": b""}

def test_route_table_exitoso(client: TestClient):
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert len(data["routes"]) == 1 # Solo la de 0.0.0.0, On-link se ignoró
    assert data["routes"][0]["gateway"] == "192.168.1.1"

def test_route_table_error_sistema(app):
    app.dependency_overrides[get_route_table_runner] = lambda: FakeRunner(1)
    custom_client = TestClient(app)
    response = custom_client.get(ENDPOINT)
    assert response.status_code == 422
    assert response.json()["error"] == "execution_failed"
