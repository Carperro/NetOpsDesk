"""Modelos de API para el Generador de Comandos."""

from pydantic import BaseModel, ConfigDict, Field

class CommandGeneratorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    command_type: str = Field(..., description="ping, tracert, ipconfig, netstat, nslookup")
    target: str | None = Field(default=None, description="IP o dominio (según comando)")
    options: list[str] = Field(default=[], description="Lista de banderas seleccionadas")

class CommandGeneratorOutput(BaseModel):
    command: str
    explanation: str
    requires_admin: bool