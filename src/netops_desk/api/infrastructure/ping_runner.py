"""Adaptador de infraestructura para ejecutar ping.exe en Windows."""

import subprocess
from netops_desk.ping import PingExecutionResult


class SubprocessPingRunner:
    """Implementación real del PingRunner usando subprocess."""

    def run(self, host: str, count: int) -> PingExecutionResult:
        try:
            # shell=False es mandatorio por seguridad. Lista de argumentos.
            result = subprocess.run(
                ["ping", "-n", str(count), "-w", "2000", host],
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
                "stderr": b"ping.exe no encontrado",
                "timed_out": False,
            }