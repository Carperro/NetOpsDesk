"""Tests de contrato HTTP para la herramienta Ping."""

import pytest
from fastapi.testclient import TestClient

from netops_desk.api.main import create_app
from netops_desk.api.routes.ping import get_ping_runner
from netops_desk.ping import PingExecutionResult

ENDPOINT = "/api/v1/tools/ping/execute"

class FakeRunner:
    def __init__(self, output: str, timed_out: bool = False):
        self.output = output
        self.timed_out = timed_out

    def run(self, host: str, count: int) -> PingExecutionResult:
        return {
            "exit_code": 0,
            "stdout": self.output.encode(),
            "stderr": b"",
            "timed_out": self.timed_out,
        }


def test_ping_exitoso(client: TestClient):
    response = client.post(ENDPOINT, json={"host": "8.8.8.8", "count": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["host"] == "8.8.8.8"
    assert data["resolved_ip"] == "8.8.8.8"
    assert data["responses"][0]["time_ms"] == 12.0


def test_ping_invalid_host(client: TestClient):
    response = client.post(ENDPOINT, json={"host": "8.8.8.8; rm -rf /"})
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_host"


def test_ping_timeout_504(app):
    # Sobreescribimos el runner para que simule un timeout
    app.dependency_overrides[get_ping_runner] = lambda: FakeRunner("", timed_out=True)
    timeout_client = TestClient(app)
    
    response = timeout_client.post(ENDPOINT, json={"host": "8.8.8.8"})
    assert response.status_code == 422 # Timeout es un DomainError (422)
    assert response.json()["error"] == "ping_timeout"
