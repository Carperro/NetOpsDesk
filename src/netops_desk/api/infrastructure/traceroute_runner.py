"""Adaptador de infraestructura para ejecutar tracert.exe en Windows."""

import subprocess
from netops_desk.traceroute import TracerouteExecutionResult


class SubprocessTracerouteRunner:
    """Implementación real del TracerouteRunner usando subprocess."""

    def run(self, host: str, max_hops: int) -> TracerouteExecutionResult:
        try:
            # Windows usa barras (/) para los flags de tracert.
            result = subprocess.run(
                ["tracert", "/h", str(max_hops), "/w", "1000", "/d", host],
                shell=False,
                capture_output=True,
                timeout=15,
            )
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": -1,
                "stdout": b"",
                "stderr": b"",
                "timed_out": True,
            }
        except FileNotFoundError:
            return {
                "exit_code": -2,
                "stdout": b"",
                "stderr": b"tracert.exe no encontrado",
                "timed_out": False,
            }