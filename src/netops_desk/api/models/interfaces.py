"""Modelos de API para Interfaces de Red."""

from pydantic import BaseModel

class InterfaceOutput(BaseModel):
    name: str
    mac_address: str | None
    ipv4: str | None
    netmask: str | None
    gateway: str | None
    dns_servers: list[str]
    is_up: bool
    speed_mbps: int

class InterfacesOutput(BaseModel):
    interfaces: list[InterfaceOutput]