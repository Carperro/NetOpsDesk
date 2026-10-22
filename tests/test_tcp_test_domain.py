"""Tests unitarios del dominio TCP Test."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.tcp_test import ErrorCode, TcpExecutionResult, execute_tcp_test


class FakeTcpRunner:
    def __init__(self, status: str, time_ms: float = 15.0):
        self.status = status
        self.time_ms = time_ms

    def run(self, host: str, port: int, timeout_ms: int) -> TcpExecutionResult:
        return {"status": self.status, "time_ms": self.time_ms}


class TestTcpDomainSuccess:
    def test_puerto_abierto(self):
        runner = FakeTcpRunner("open", 12.5)
        result = execute_tcp_test(host="8.8.8.8", port=443, runner=runner)
        assert result["status"] == "open"
        assert result["time_ms"] == 12.5

    def test_puerto_cerrado(self):
        runner = FakeTcpRunner("closed", 1.0)
        result = execute_tcp_test(host="8.8.8.8", port=80, runner=runner)
        assert result["status"] == "closed"

    def test_puerto_filtrado(self):
        runner = FakeTcpRunner("filtered", 3000.0)
        result = execute_tcp_test(host="8.8.8.8", port=8080, runner=runner)
        assert result["status"] == "filtered"


class TestTcpDomainErrors:
    def test_host_invalido(self):
        runner = FakeTcpRunner("open")
        with pytest.raises(DomainError) as exc:
            execute_tcp_test(host="8.8.8.8; rm -rf /", port=80, runner=runner)
        assert exc.value.code == ErrorCode.INVALID_HOST

    def test_puerto_invalido(self):
        runner = FakeTcpRunner("open")
        for port in [0, 65536, -1]:
            with pytest.raises(DomainError) as exc:
                execute_tcp_test(host="8.8.8.8", port=port, runner=runner)
            assert exc.value.code == ErrorCode.INVALID_PORT

    def test_timeout_invalido(self):
        runner = FakeTcpRunner("open")
        for timeout in [499, 10001, 0]:
            with pytest.raises(DomainError) as exc:
                execute_tcp_test(host="8.8.8.8", port=80, timeout_ms=timeout, runner=runner)
            assert exc.value.code == ErrorCode.INVALID_TIMEOUT