"""Adaptador de infraestructura para route print -4."""

import subprocess
from netops_desk.route_table import RouteExecutionResult

class SubprocessRouteTableRunner:
    def run(self) -> RouteExecutionResult:
        try:
            res = subprocess.run(
                ["cmd", "/c", "route", "print", "-4"],
                shell=False,
                capture_output=True,
                timeout=10,
            )
            return {"exit_code": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"exit_code": -1, "stdout": b"", "stderr": b"Execution failed"}