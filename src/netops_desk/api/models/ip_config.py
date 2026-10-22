"""Modelos de API para Asistente de Configuración IP."""

from pydantic import BaseModel, ConfigDict, Field

class IpConfigInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., description="renew_dhcp, set_dhcp, set_static o set_dns")
    interface_name: str = Field(..., description="Nombre de la interfaz")
    ip: str | None = Field(default=None)
    mask: str | None = Field(default=None)
    gateway: str | None = Field(default=None)
    dns_ip: str | None = Field(default=None)

class IpConfigOutput(BaseModel):
    action: str
    command: str
    explanation: str