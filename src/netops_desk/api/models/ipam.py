"""Modelos de API para el Gestor de Direcciones IP (IPAM)."""

from pydantic import BaseModel, ConfigDict, Field

class IpamInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    ip_address: str = Field(..., description="Dirección IPv4")
    status: str = Field(..., description="Estado: available, assigned o reserved")
    assigned_to: str = Field(default="", description="Equipo o persona asignada")
    notes: str = Field(default="", description="Observaciones")

class IpamOutput(BaseModel):
    id: int
    ip_address: str
    status: str
    assigned_to: str
    notes: str