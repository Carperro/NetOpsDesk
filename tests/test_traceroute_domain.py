"""Tests unitarios del dominio Traceroute con FakeRunner."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.traceroute import ErrorCode, TracerouteExecutionResult, execute_traceroute


class FakeTracerouteRunner:
    def __init__(self, output: str, exit_code: int = 0, timed_out: bool = False):
        self.output = output
        self.exit_code = exit_code
        self.timed_out = timed_out

    def run(self, host: str, max_hops: int) -> TracerouteExecutionResult:
        return {
            "exit_code": self.exit_code,
            "stdout": self.output.encode("utf-8"),
            "stderr": b"",
            "timed_out": self.timed_out,
        }


class TestTracerouteSuccess:
    def test_parseo_basico_ingles(self):
        output = (
            "Tracing route to 8.8.8.8 over a maximum of 30 hops\n\n"
            "  1     1 ms     1 ms     1 ms  192.168.1.1\n"
            "  2     *        *        *     Request timed out.\n"
            "  3    12 ms    11 ms    10 ms  10.0.0.1\n"
        )
        runner = FakeTracerouteRunner(output)
        result = execute_traceroute(host="8.8.8.8", max_hops=3, runner=runner)
        
        assert result["resolved_ip"] == "8.8.8.8"
        assert len(result["hops"]) == 3
        
        # Salto 1
        assert result["hops"][0]["hop_number"] == 1
        assert result["hops"][0]["ip"] == "192.168.1.1"
        assert result["hops"][0]["times_ms"] == [1.0, 1.0, 1.0]

        # Salto 2 (timeout)
        assert result["hops"][1]["hop_number"] == 2
        assert result["hops"][1]["ip"] is None
        assert result["hops"][1]["times_ms"] == []

        # Salto 3
        assert result["hops"][2]["hop_number"] == 3
        assert result["hops"][2]["ip"] == "10.0.0.1"
        assert result["hops"][2]["times_ms"] == [12.0, 11.0, 10.0]

    def test_parseo_espanol_y_parcial(self):
        output = (
            "Traza a 8.8.8.8 sobre un máximo de 30 saltos\n\n"
            "  1    <1 ms    <1 ms    <1 ms  192.168.0.1\n"
            "  2    15 ms     *       14 ms  10.0.0.1\n"
        )
        runner = FakeTracerouteRunner(output)
        result = execute_traceroute(host="8.8.8.8", runner=runner)
        
        assert result["hops"][0]["times_ms"] == [0.0, 0.0, 0.0]
        # Salto parcial: solo 2 respuestas
        assert result["hops"][1]["times_ms"] == [15.0, 14.0]
        assert result["hops"][1]["ip"] == "10.0.0.1"

    def test_resolved_ip_desde_cabecera(self):
        output = (
            "Tracing route to google.com [142.250.78.142]\n"
            "  1     1 ms     1 ms     1 ms  192.168.1.1\n"
        )
        runner = FakeTracerouteRunner(output)
        result = execute_traceroute(host="google.com", runner=runner)
        
        assert result["resolved_ip"] == "142.250.78.142"


class TestTracerouteErrors:
    def test_timeout_del_proceso(self):
        runner = FakeTracerouteRunner("", timed_out=True)
        with pytest.raises(DomainError) as exc:
            execute_traceroute(host="8.8.8.8", runner=runner)
        assert exc.value.code == ErrorCode.TRACEROUTE_TIMEOUT

    def test_fallo_de_ejecucion(self):
        runner = FakeTracerouteRunner("", exit_code=2)
        with pytest.raises(DomainError) as exc:
            execute_traceroute(host="8.8.8.8", runner=runner)
        assert exc.value.code == ErrorCode.EXECUTION_FAILED

    def test_host_invalido(self):
        runner = FakeTracerouteRunner("")
        with pytest.raises(DomainError) as exc:
            execute_traceroute(host="google.com; rm -rf /", runner=runner)
        assert exc.value.code == ErrorCode.INVALID_HOST

    def test_max_hops_invalido(self):
        runner = FakeTracerouteRunner("")
        with pytest.raises(DomainError) as exc:
            execute_traceroute(host="8.8.8.8", max_hops=31, runner=runner)
        assert exc.value.code == ErrorCode.INVALID_MAX_HOPS