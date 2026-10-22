"""Modelos de API para el Visor ARP."""

from pydantic import BaseModel


class ArpEntryOutput(BaseModel):
    interface_ip: str
    ip_address: str
    mac_address: str
    entry_type: str


class ArpOutput(BaseModel):
    entries: list[ArpEntryOutput]