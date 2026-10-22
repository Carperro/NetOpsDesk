"""Adaptador de infraestructura para consultas DNS usando dnspython."""

import time
import dns.resolver
import dns.exception

from netops_desk.exceptions import DomainError
from netops_desk.dns_test import ErrorCode, DnsExecutionResult


class DnspythonRunner:
    """Implementación real del DnsRunner usando la librería dnspython."""

    def run(self, domain: str, record_type: str, resolver: str | None) -> DnsExecutionResult:
        custom_resolver = dns.resolver.Resolver()
        
        # Si el cliente proveyó un resolver (ej. 8.8.8.8), lo usamos
        if resolver:
            custom_resolver.nameservers = [resolver]

        # Límite duro de 5 segundos por consulta
        custom_resolver.timeout = 5.0
        custom_resolver.lifetime = 5.0

        start_time = time.perf_counter()

        try:
            answers = custom_resolver.resolve(domain, record_type)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            records = []
            for rdata in answers:
                # Para MX, TXT, etc., el string ya viene formateado.
                # Limpiamos las comillas que dnspython agrega a los TXT
                records.append(rdata.to_text().strip('"'))

            return {
                "status": "success",
                "time_ms": round(elapsed_ms, 2),
                "records": records,
            }

        except dns.resolver.NXDOMAIN:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {"status": "nxdomain", "time_ms": round(elapsed_ms, 2), "records": []}

        except dns.resolver.NoAnswer:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {"status": "success", "time_ms": round(elapsed_ms, 2), "records": []}

        except (dns.resolver.LifetimeTimeout, dns.exception.Timeout) as exc:
            raise DomainError(
                message="La consulta DNS excedió el tiempo límite.",
                code=ErrorCode.DNS_TIMEOUT,
            ) from exc

        except Exception as exc:
            raise DomainError(
                message="No se pudo completar la consulta DNS.",
                code=ErrorCode.EXECUTION_FAILED,
            ) from exc