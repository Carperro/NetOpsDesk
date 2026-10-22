"""Tests unitarios del dominio DNS con FakeRunner."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.dns_test import ErrorCode, DnsExecutionResult, execute_dns_test


class FakeDnsRunner:
    def __init__(self, status: str = "success", records: list[str] | None = None):
        self.status = status
        # Usar validación explícita con None, no truthiness
        self.records = records if records is not None else ["1.1.1.1"]

    def run(self, domain: str, record_type: str, resolver: str | None) -> DnsExecutionResult:
        return {"status": self.status, "time_ms": 12.5, "records": self.records}


class TestDnsDomainSuccess:
    def test_consulta_exitosa(self):
        runner = FakeDnsRunner("success", ["8.8.8.8"])
        result = execute_dns_test(domain="google.com", record_type="a", runner=runner)
        
        assert result["domain"] == "google.com"
        assert result["record_type"] == "A"
        assert result["status"] == "success"
        assert result["records"] == ["8.8.8.8"]

    def test_resolver_por_defecto(self):
        runner = FakeDnsRunner()
        result = execute_dns_test(domain="test.com", record_type="MX", runner=runner)
        assert result["resolver"] == "system"

    def test_resolver_custom(self):
        runner = FakeDnsRunner()
        result = execute_dns_test(domain="test.com", record_type="MX", resolver="8.8.8.8", runner=runner)
        assert result["resolver"] == "8.8.8.8"

    def test_dominio_inexistente(self):
        runner = FakeDnsRunner("nxdomain", [])
        result = execute_dns_test(domain="no-existe.com", record_type="A", runner=runner)
        assert result["status"] == "nxdomain"
        assert result["records"] == []


class TestDnsDomainErrors:
    def test_dominio_invalido(self):
        runner = FakeDnsRunner()
        with pytest.raises(DomainError) as exc:
            execute_dns_test(domain="http://google.com", record_type="A", runner=runner)
        assert exc.value.code == ErrorCode.INVALID_DOMAIN

    def test_record_type_invalido(self):
        runner = FakeDnsRunner()
        with pytest.raises(DomainError) as exc:
            execute_dns_test(domain="google.com", record_type="HACK", runner=runner)
        assert exc.value.code == ErrorCode.INVALID_RECORD_TYPE

    def test_resolver_invalido(self):
        runner = FakeDnsRunner()
        with pytest.raises(DomainError) as exc:
            execute_dns_test(domain="google.com", record_type="A", resolver="8.8.8.999", runner=runner)
        assert exc.value.code == ErrorCode.INVALID_RESOLVER