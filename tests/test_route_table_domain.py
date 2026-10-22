"""Tests unitarios de dominio para las herramientas de rutas (10 y 14)."""

import pytest
from netops_desk.exceptions import DomainError

# Herramienta 10: Analizador de Gateway
from netops_desk.route_analyzer import (
    ErrorCode as AnalyzerErrorCode, 
    execute_route_analyzer, 
    RouteExecutionResult as AnalyzerResult
)

# Herramienta 14: Visor de Tabla de Rutas
from netops_desk.route_table import (
    ErrorCode as TableErrorCode, 
    execute_route_table, 
    RouteExecutionResult as TableResult
)


# ==========================================
# Tests para Herramienta 10 (Route Analyzer)
# ==========================================

class FakeAnalyzerRunner:
    def __init__(self, ipconfig: str, route: str, exit_code: int = 0):
        self.ipconfig = ipconfig
        self.route = route
        self.exit_code = exit_code

    def run(self) -> AnalyzerResult:
        return {
            "ipconfig_stdout": self.ipconfig.encode("utf-8"),
            "route_stdout": self.route.encode("utf-8"),
            "exit_code": self.exit_code,
        }


class TestRouteAnalyzerSuccess:
    def test_parseo_ingles(self):
        ipconfig = (
            "Windows IP Configuration\n"
            "   Default Gateway . . . . . . . . . : 192.168.1.1\n"
        )
        route = (
            "===========================================================================\n"
            "IPv4 Route Table\n"
            "===========================================================================\n"
            "Network Destination        Netmask          Gateway       Interface  Metric\n"
            "          0.0.0.0          0.0.0.0      192.168.1.1     192.168.1.50     25\n"
        )
        runner = FakeAnalyzerRunner(ipconfig, route)
        result = execute_route_analyzer(runner=runner)
        
        assert result["default_gateway"] == "192.168.1.1"
        assert len(result["routes"]) == 1
        assert result["routes"][0]["destination"] == "0.0.0.0"
        assert result["routes"][0]["metric"] == 25

    def test_parseo_espanol(self):
        ipconfig = (
            "Configuración IP de Windows\n"
            "   Puerta de enlace predeterminada . . . : 10.0.0.1\n"
        )
        route = (
            "          0.0.0.0          0.0.0.0         10.0.0.1        10.0.0.50     10\n"
        )
        runner = FakeAnalyzerRunner(ipconfig, route)
        result = execute_route_analyzer(runner=runner)
        
        assert result["default_gateway"] == "10.0.0.1"
        assert result["routes"][0]["gateway"] == "10.0.0.1"


class TestRouteAnalyzerErrors:
    def test_fallo_comando(self):
        runner = FakeAnalyzerRunner("", "", exit_code=1)
        with pytest.raises(DomainError) as exc:
            execute_route_analyzer(runner=runner)
        assert exc.value.code == AnalyzerErrorCode.EXECUTION_FAILED

    def test_salida_irreconocible(self):
        runner = FakeAnalyzerRunner("Basura", "Basura")
        with pytest.raises(DomainError) as exc:
            execute_route_analyzer(runner=runner)
        assert exc.value.code == AnalyzerErrorCode.EXECUTION_FAILED


# ==========================================
# Tests para Herramienta 14 (Route Table)
# ==========================================

class FakeTableRunner:
    def __init__(self, exit_code: int = 0):
        self.exit_code = exit_code

    def run(self) -> TableResult:
        if self.exit_code != 0: 
            return {"exit_code": self.exit_code, "stdout": b"", "stderr": b""}
        output = (
            "          0.0.0.0          0.0.0.0      192.168.1.1     192.168.1.50     25\n"
            "        127.0.0.0        255.0.0.0         On-link         127.0.0.1    331\n"
        )
        return {"exit_code": 0, "stdout": output.encode("cp850"), "stderr": b""}


class TestRouteTableSuccess:
    def test_route_table_parseo(self):
        res = execute_route_table(runner=FakeTableRunner())
        # Verifica que ignoró la fila "On-link"
        assert len(res["routes"]) == 1 
        assert res["routes"][0]["gateway"] == "192.168.1.1"
        assert res["routes"][0]["metric"] == 25


class TestRouteTableErrors:
    def test_route_table_error(self):
        with pytest.raises(DomainError) as exc:
            execute_route_table(runner=FakeTableRunner(exit_code=1))
        assert exc.value.code == TableErrorCode.EXECUTION_FAILED