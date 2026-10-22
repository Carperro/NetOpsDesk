"""Adaptador para obtener interfaces de red (psutil + ipconfig)."""

import ipaddress
import re
import socket
import subprocess
import psutil
from netops_desk.interfaces import InterfaceInfo
from netops_desk.exceptions import DomainError

class PsutilInterfacesRunner:
    def run(self) -> list[InterfaceInfo]:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        # Extraer Gateway y DNS usando ipconfig /all
        try:
            ipconfig = subprocess.run(
                ["ipconfig", "/all"],
                shell=False,
                capture_output=True,
                timeout=10,
                check=True,
            ).stdout.decode("utf-8", errors="replace")
        except (OSError, subprocess.SubprocessError) as exc:
            raise DomainError(
                message="No se pudo consultar la configuración de interfaces del sistema.",
                code="execution_failed",
            ) from exc
            
        gateways = re.findall(r"(?:Default Gateway|Puerta de enlace predeterminada)[^\d]*([0-9\.]+)", ipconfig)
        dns_servers = re.findall(r"(?:DNS Servers|Servidores DNS)[^\d]*([0-9\.]+)", ipconfig)
        
        # El primer gateway válido encontrado
        main_gateway = gateways[0] if gateways else None

        interfaces = []
        for name, snics in addrs.items():
            ipv4 = None
            netmask = None
            mac = None
            
            for snic in snics:
                if snic.family == socket.AF_INET:
                    ipv4 = snic.address
                    netmask = snic.netmask
                elif snic.family == psutil.AF_LINK:
                    mac = snic.address

            stat = stats.get(name)
            is_up = stat.isup if stat else False
            speed = stat.speed if stat else 0

            # Asignar el gateway principal a todas las IPv4 (simplificación)
            # En un caso real, se verificaría si la IP es de la misma subred que el gateway
            gw = main_gateway if ipv4 and not ipv4.startswith("127.") else None

            interfaces.append({
                "name": name,
                "mac_address": mac,
                "ipv4": ipv4,
                "netmask": netmask,
                "gateway": gw,
                "dns_servers": dns_servers if gw else [],
                "is_up": is_up,
                "speed_mbps": speed,
            })
            
        return interfaces
