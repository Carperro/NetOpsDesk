"""Modelos de API para el Analizador MAC."""

from pydantic import BaseModel, ConfigDict, Field

class MacAnalyzerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mac: str = Field(..., description="Dirección MAC (ej. 00:1A:2B:3C:4D:5E)")

class MacAnalyzerOutput(BaseModel):
    mac_original: str
    mac_normalized: str
    vendor: str