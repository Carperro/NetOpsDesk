"""Modelos de API para el Catálogo de Puertos."""

from pydantic import BaseModel

class PortRecordOutput(BaseModel):
    port: int
    protocol: str
    service: str
    description: str

class PortCatalogOutput(BaseModel):
    ports: list[PortRecordOutput]