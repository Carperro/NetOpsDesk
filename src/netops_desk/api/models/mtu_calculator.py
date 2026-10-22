"""Modelos de API para la Calculadora MTU."""

from pydantic import BaseModel, ConfigDict, Field

class MtuInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    mtu: int = Field(default=1500, ge=68, le=9000, description="Tamaño máximo del paquete")
    ip_version: str = Field(..., description="ipv4 o ipv6")
    transport: str = Field(..., description="tcp o udp")
    tunnel: str = Field(..., description="none, gre, ipsec o wireguard")

class MtuOutput(BaseModel):
    mtu: int
    ip_version: str
    transport: str
    tunnel: str
    mss: int
    ip_header_size: int
    transport_header_size: int
    tunnel_header_size: int
    warnings: list[str]