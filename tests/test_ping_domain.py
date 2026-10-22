"""Tests unitarios del dominio Ping con un FakeRunner inyectado."""

import pytest

from netops_desk.exceptions import DomainError
from netops_desk.ping import ErrorCode, PingExecutionResult, PingRunner, execute_ping


class FakePingRunner:
    """Runner falso para inyectar respuestas controladas en los tests."""

    def __init__(self, output: str, exit_code: int = 0, timed_out: bool = False):
        self.output = output
        self.exit_code = exit_code
        self.timed_out = timed_out

    def run(self, host: str, count: int) -> PingExecutionResult:
        return {
            "exit_code": self.exit_code,
            "stdout": self.output.encode("utf-8"),
            "stderr": b"",
            "timed_out": self.timed_out,
        }


class TestPingDomainSuccess:
    def test_ping_exitoso_ingles(self):
        output = (
            "Pinging 8.8.8.8 with 32 bytes of data:\n"
            "Reply from 8.8.8.8: bytes=32 time=12ms TTL=117\n"
            "Reply from 8.8.8.8: bytes=32 time=15ms TTL=117\n"
            "Reply from 8.8.8.8: bytes=32 time<1ms TTL=117\n"
        )
        runner = FakePingRunner(output)
        result = execute_ping(host="8.8.8.8", count=3, runner=runner)
        
        assert result["resolved_ip"] == "8.8.8.8"
        assert result["packets_sent"] == 3
        assert result["packets_received"] == 3
        assert result["packet_loss_percent"] == 0.0
        assert result["min_ms"] == 0.0
        assert result["max_ms"] == 15.0
        assert result["avg_ms"] == 9.0
        assert len(result["responses"]) == 3
        assert result["responses"][0] == {"seq": 1, "time_ms": 12.0}
        assert result["responses"][2] == {"seq": 3, "time_ms": 0.0}

    def test_ping_exitoso_espanol(self):
        output = (
            "Haciendo ping a 8.8.8.8 con 32 bytes de datos:\n"
            "Respuesta desde 8.8.8.8: bytes=32 tiempo=12ms TTL=117\n"
        )
        runner = FakePingRunner(output)
        result = execute_ping(host="8.8.8.8", count=1, runner=runner)
        
        assert result["resolved_ip"] == "8.8.8.8"
        assert result["responses"][0]["time_ms"] == 12.0

    def test_ping_con_perdida(self):
        output = (
            "Pinging 8.8.8.8 with 32 bytes of data:\n"
            "Reply from 8.8.8.8: bytes=32 time=12ms TTL=117\n"
            "Request timed out.\n"
            "Reply from 8.8.8.8: bytes=32 time=15ms TTL=117\n"
        )
        runner = FakePingRunner(output)
        result = execute_ping(host="8.8.8.8", count=3, runner=runner)
        
        assert result["packets_sent"] == 3
        assert result["packets_received"] == 2
        assert result["packet_loss_percent"] == pytest.approx(33.33, rel=1e-3)
        assert len(result["responses"]) == 2
        # Seq sin huecos
        assert result["responses"][0]["seq"] == 1
        assert result["responses"][1]["seq"] == 2

    def test_ping_totalmente_perdido(self):
        output = (
            "Pinging 192.0.2.10 with 32 bytes of data:\n"
            "Request timed out.\n"
            "Request timed out.\n"
            "Request timed out.\n"
            "Request timed out.\n"
        )
        runner = FakePingRunner(output)
        result = execute_ping(host="192.0.2.10", count=4, runner=runner)
        
        assert result["packets_received"] == 0
        assert result["packet_loss_percent"] == 100.0
        assert result["min_ms"] is None
        assert result["max_ms"] is None
        assert result["avg_ms"] is None
        assert result["responses"] == []


class TestPingDomainErrors:
    def test_timeout_del_proceso(self):
        runner = FakePingRunner("", timed_out=True)
        with pytest.raises(DomainError) as exc:
            execute_ping(host="8.8.8.8", runner=runner)
        assert exc.value.code == ErrorCode.PING_TIMEOUT

    def test_fallo_de_ejecucion(self):
        runner = FakePingRunner("'ping' no se reconoce como un comando interno.", exit_code=2)
        with pytest.raises(DomainError) as exc:
            execute_ping(host="8.8.8.8", runner=runner)
        assert exc.value.code == ErrorCode.EXECUTION_FAILED

    def test_inyeccion_de_comandos_host(self):
        runner = FakePingRunner("")
        hosts_invalidos = [
            "8.8.8.8 & calc.exe",
            "google.com; rm -rf /",
            "8.8.8.8 | cat /etc/passwd",
            "host inyectado",
        ]
        for host in hosts_invalidos:
            with pytest.raises(DomainError) as exc:
                execute_ping(host=host, runner=runner)
            assert exc.value.code == ErrorCode.INVALID_HOST

    def test_count_invalido(self):
        runner = FakePingRunner("")
        for count in [0, 11, -1]:
            with pytest.raises(DomainError) as exc:
                execute_ping(host="8.8.8.8", count=count, runner=runner)
            assert exc.value.code == ErrorCode.INVALID_COUNT