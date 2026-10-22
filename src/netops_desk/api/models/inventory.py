"""Modelos de API para el Inventario de Dispositivos."""

from pydantic import BaseModel, ConfigDict, Field

class DeviceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Nombre del dispositivo")
    ip_address: str = Field(..., description="Dirección IPv4")
    device_type: str = Field(default="", description="Tipo de equipo (Router, PC, etc.)")
    location: str = Field(default="", description="Ubicación física")
    notes: str = Field(default="", description="Observaciones")

class DeviceOutput(BaseModel):
    id: int
    name: str
    ip_address: str
    device_type: str
    location: str
    notes: str