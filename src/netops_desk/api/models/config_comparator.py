"""Modelos de API para el Comparador de Configuraciones."""

from pydantic import BaseModel, ConfigDict, Field

class ConfigComparatorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    config_a: str = Field(
        ..., 
        max_length=50000, 
        description="Configuración original (máx 50.000 caracteres)"
    )
    config_b: str = Field(
        ..., 
        max_length=50000, 
        description="Configuración nueva (máx 50.000 caracteres)"
    )

class ConfigComparatorOutput(BaseModel):
    has_changes: bool
    diff_lines: list[str]