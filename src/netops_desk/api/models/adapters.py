"""Modelos de API para Estado de Adaptadores."""

from pydantic import BaseModel

class AdapterOutput(BaseModel):
    name: str
    is_up: bool
    speed_mbps: int
    mtu: int
    is_multicast: bool

class AdaptersOutput(BaseModel):
    adapters: list[AdapterOutput]