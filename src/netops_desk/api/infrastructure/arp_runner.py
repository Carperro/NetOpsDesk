"""Adaptador de infraestructura para ejecutar arp -a."""

import subprocess
from netops_desk.arp_viewer import ArpExecutionResult

class SubprocessArpRunner:
    def run(self) -> ArpExecutionResult:
        try:
            res = subprocess.run(
                ["cmd", "/c", "arp", "-a"], # Usamos cmd /c para forzar la consola
                shell=False,
                capture_output=True,
                timeout=10,
            )
            return {"exit_code": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"exit_code": -1, "stdout": b"", "stderr": b"Execution failed"}