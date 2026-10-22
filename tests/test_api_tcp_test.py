"""Tests de contrato HTTP para la Prueba de puertos TCP."""

import pytest
from fastapi.testclient import TestClient

from netops_desk.api.main import create_app
from netops_desk.api.routes.tcp_test import get_tcp_runner
from netops_desk.exceptions import DomainError
from netops_desk.tcp_test import ErrorCode, TcpExecutionResult

ENDPOINT = "/api/v1/tools/tcp-test/execute"


class FakeTcpRunner:
    def __init__(self, status: str = "open"):
        self.status = status

    def run(self, host: str, port: int, timeout_ms: int) -> TcpExecutionResult:
        if self.status == "error":
            raise DomainError("Error de red", code=ErrorCode.HOST_UNREACHABLE)
        return {"status": self.status, "time_ms": 15.0}


def test_puerto_abierto(client: TestClient):
    response = client.post(ENDPOINT, json={"host": "8.8.8.8", "port": 443})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "open"
    assert data["time_ms"] == 15.0


def test_puerto_cerrado_o_filtrado(app):
    app.dependency_overrides[get_tcp_runner] = lambda: FakeTcpRunner("filtered")
    custom_client = TestClient(app)
    
    response = custom_client.post(ENDPOINT, json={"host": "8.8.8.8", "port": 8080})
    assert response.status_code == 200
    assert response.json()["status"] == "filtered"


def test_error_dns(app):
    app.dependency_overrides[get_tcp_runner] = lambda: FakeTcpRunner("error")
    custom_client = TestClient(app)
    
    response = custom_client.post(ENDPOINT, json={"host": "no-existe.com", "port": 80})
    assert response.status_code == 422
    assert response.json()["error"] == "host_unreachable"


def test_puerto_invalido(client: TestClient):
    response = client.post(ENDPOINT, json={"host": "8.8.8.8", "port": 99999})
    assert response.status_code == 422
    # Pydantic atrapa esto antes del dominio
    assert response.json()["error"] == "invalid_value"
