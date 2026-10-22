"""Modelos de API para el Analizador de Rutas."""

from pydantic import BaseModel


class RouteEntryOutput(BaseModel):
    destination: str
    netmask: str
    gateway: str
    interface: str
    metric: int


class RouteAnalyzerOutput(BaseModel):
    default_gateway: str | None
    routes: list[RouteEntryOutput]