"""Catálogo estático de puertos y protocolos."""

from __future__ import annotations
from typing import TypedDict

__all__ = ["PortRecord", "search_ports"]

class PortRecord(TypedDict):
    port: int
    protocol: str
    service: str
    description: str

# Dataset estático (puede ampliarse en el futuro)
PORT_DATABASE: list[PortRecord] = [
    {"port": 20, "protocol": "TCP", "service": "FTP-Data", "description": "File Transfer Protocol (Data)"},
    {"port": 21, "protocol": "TCP", "service": "FTP", "description": "File Transfer Protocol (Control)"},
    {"port": 22, "protocol": "TCP", "service": "SSH", "description": "Secure Shell"},
    {"port": 23, "protocol": "TCP", "service": "Telnet", "description": "Telnet (Inseguro)"},
    {"port": 25, "protocol": "TCP", "service": "SMTP", "description": "Simple Mail Transfer Protocol"},
    {"port": 53, "protocol": "UDP/TCP", "service": "DNS", "description": "Domain Name System"},
    {"port": 67, "protocol": "UDP", "service": "DHCP-Server", "description": "Dynamic Host Configuration Protocol"},
    {"port": 68, "protocol": "UDP", "service": "DHCP-Client", "description": "Dynamic Host Configuration Protocol"},
    {"port": 80, "protocol": "TCP", "service": "HTTP", "description": "Hypertext Transfer Protocol (World Wide Web)"},
    {"port": 110, "protocol": "TCP", "service": "POP3", "description": "Post Office Protocol v3"},
    {"port": 123, "protocol": "UDP", "service": "NTP", "description": "Network Time Protocol"},
    {"port": 143, "protocol": "TCP", "service": "IMAP", "description": "Internet Message Access Protocol"},
    {"port": 161, "protocol": "UDP", "service": "SNMP", "description": "Simple Network Management Protocol"},
    {"port": 443, "protocol": "TCP", "service": "HTTPS", "description": "HTTP Secure (SSL/TLS)"},
    {"port": 445, "protocol": "TCP", "service": "SMB", "description": "Server Message Block (Windows File Sharing)"},
    {"port": 3306, "protocol": "TCP", "service": "MySQL", "description": "Base de datos MySQL / MariaDB"},
    {"port": 3389, "protocol": "TCP", "service": "RDP", "description": "Remote Desktop Protocol (Escritorio Remoto)"},
    {"port": 5432, "protocol": "TCP", "service": "PostgreSQL", "description": "Base de datos PostgreSQL"},
    {"port": 8080, "protocol": "TCP", "service": "HTTP-Alt", "description": "HTTP alternativo (proxies, dev)"},
    {"port": 8443, "protocol": "TCP", "service": "HTTPS-Alt", "description": "HTTPS alternativo"}
]

def search_ports(query: str = "") -> list[PortRecord]:
    """Filtra el catálogo por número de puerto o nombre de servicio."""
    q = query.strip().lower()
    if not q:
        return PORT_DATABASE
    
    return [
        rec for rec in PORT_DATABASE
        if q in str(rec["port"]) or q in rec["service"].lower()
    ]