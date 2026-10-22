"""Adaptador de infraestructura para obtener configuración de red en Windows."""

import subprocess
from netops_desk.route_analyzer import RouteExecutionResult


class SubprocessRouteRunner:
    """Implementación real del RouteRunner usando subprocess."""

    def run(self) -> RouteExecutionResult:
        try:
            ipconfig = subprocess.run(
                ["ipconfig"],
                shell=False,
                capture_output=True,
                timeout=10,
            )
            # Forzamos IPv4 para no parsear tablas de IPv6
            route = subprocess.run(
                ["route", "print", "-4"],
                shell=False,
                capture_output=True,
                timeout=10,
            )
            
            # Consideramos exitoso si al menos route print devolvió 0
            exit_code = 0 if route.returncode == 0 else 1
            
            return {
                "ipconfig_stdout": ipconfig.stdout,
                "route_stdout": route.stdout,
                "exit_code": exit_code,
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {
                "ipconfig_stdout": b"",
                "route_stdout": b"",
                "exit_code": -1,
            }