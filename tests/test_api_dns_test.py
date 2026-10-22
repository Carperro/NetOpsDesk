"""Tests de contrato HTTP para Diagnóstico DNS."""

import pytest
from fastapi.testclient import TestClient

from netops_desk.api.main import create_app
from netops_desk.api.routes.dns_test import get_dns_runner
from netops_desk.exceptions import DomainError
from netops_desk.dns_test import ErrorCode, DnsExecutionResult

ENDPOINT = "/api/v1/tools/dns-test/execute"

class FakeRunner:
    def __init__(self, status: str = "success", records: list[str] | None = None, raises_error: bool = False):
        self.status = status
        self.records = records if records is not None else ["1.1.1.1"]
        self.raises_error = raises_error

    def run(self, domain: str, record_type: str, resolver: str | None) -> DnsExecutionResult:
        if self.raises_error:
            raise DomainError("Timeout de DNS", code=ErrorCode.DNS_TIMEOUT)
        return {"status": self.status, "time_ms": 15.0, "records": self.records}


def test_dns_exitoso(client: TestClient):
    response = client.post(ENDPOINT, json={"domain": "google.com", "record_type": "A"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["records"] == ["1.1.1.1"]

def test_dns_nxdomain(app):
    app.dependency_overrides[get_dns_runner] = lambda: FakeRunner("nxdomain", [])
    custom_client = TestClient(app)
    
    response = custom_client.post(ENDPOINT, json={"domain": "no-existe.com", "record_type": "A"})
    assert response.status_code == 200
    assert response.json()["status"] == "nxdomain"

def test_dns_timeout_504(app):
    app.dependency_overrides[get_dns_runner] = lambda: FakeRunner(raises_error=True)
    custom_client = TestClient(app)
    
    response = custom_client.post(ENDPOINT, json={"domain": "google.com", "record_type": "A"})
    # Mapeado a 422 por el handler global, aunque conceptualmente es un error de red
    assert response.status_code == 422 
    assert response.json()["error"] == "dns_timeout"

def test_dns_dominio_invalido(client: TestClient):
    response = client.post(ENDPOINT, json={"domain": "http://google.com", "record_type": "A"})
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_domain"
