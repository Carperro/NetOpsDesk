"""Adaptador de infraestructura para probar puertos TCP usando sockets."""

import socket
import time

from netops_desk.exceptions import DomainError
from netops_desk.tcp_test import ErrorCode, TcpExecutionResult


class SocketTcpRunner:
    """Implementación real del TcpRunner usando la librería socket nativa."""

    def run(self, host: str, port: int, timeout_ms: int) -> TcpExecutionResult:
        timeout_s = timeout_ms / 1000.0
        start_time = time.perf_counter()

        try:
            # create_connection maneja la resolución DNS y el handshake TCP
            with socket.create_connection((host, port), timeout=timeout_s):
                pass  # Si llegamos acá, el puerto está abierto
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {"status": "open", "time_ms": round(elapsed_ms, 2)}

        except ConnectionRefusedError:
            # El host respondió con un RST (puerto cerrado)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {"status": "closed", "time_ms": round(elapsed_ms, 2)}

        except socket.timeout:
            # No hubo respuesta en el tiempo estipulado
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {"status": "filtered", "time_ms": round(elapsed_ms, 2)}

        except socket.gaierror as exc:
            # Error de resolución DNS (el dominio no existe)
            raise DomainError(
                message="No se pudo resolver el nombre de dominio.",
                code=ErrorCode.HOST_UNREACHABLE,
            ) from exc

        except OSError as exc:
            # Otros errores de red (ej. ruta inalcanzable)
            raise DomainError(
                message="El host no es alcanzable en la red.",
                code=ErrorCode.HOST_UNREACHABLE,
            ) from exc