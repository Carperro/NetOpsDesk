"""Tests de contrato HTTP para la herramienta Traceroute."""

import pytest
from fastapi.testclient import TestClient

from netops_desk.api.main import create_app
from netops_desk.api.routes.traceroute import get_traceroute_runner
from netops_desk.traceroute import TracerouteExecutionResult

ENDPOINT = "/api/v1/tools/traceroute/execute"

class FakeRunner:
    def __init__(self, output: str, timed_out: bool = False):
        self.output = output
        self.timed_out = timed_out

    def run(self, host: str, max_hops: int) -> TracerouteExecutionResult:
        return {
            "exit_code": 0,
            "stdout": self.output.encode(),
            "stderr": b"",
            "timed_out": self.timed_out,
        }


def test_traceroute_exitoso(client: TestClient):
    response = client.post(ENDPOINT, json={"host": "8.8.8.8", "max_hops": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["host"] == "8.8.8.8"
    assert len(data["hops"]) == 1
    assert data["hops"][0]["ip"] == "192.168.1.1"


def test_traceroute_invalid_host(client: TestClient):
    response = client.post(ENDPOINT, json={"host": "8.8.8.8 & dir"})
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_host"


def test_traceroute_timeout(app):
    app.dependency_overrides[get_traceroute_runner] = lambda: FakeRunner("", timed_out=True)
    timeout_client = TestClient(app)
    
    response = timeout_client.post(ENDPOINT, json={"host": "8.8.8.8"})
    assert response.status_code == 422 # DomainError atrapado por handler global
    assert response.json()["error"] == "traceroute_timeout"
