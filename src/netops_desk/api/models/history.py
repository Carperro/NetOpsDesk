"""Modelos de API para el Historial."""

from pydantic import BaseModel, ConfigDict, Field

class HistoryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tool_name: str = Field(..., description="Nombre de la herramienta")
    action: str = Field(..., description="Acción realizada")
    result_status: str = Field(default="unknown", description="Estado del resultado")
    details: str = Field(default="", description="Detalles adicionales")

class HistoryOutput(BaseModel):
    id: int
    tool_name: str
    action: str
    result_status: str
    details: str
    created_at: str