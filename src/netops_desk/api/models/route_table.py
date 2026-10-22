"""Modelos de API para la Tabla de Rutas."""

from pydantic import BaseModel

class RouteEntryOutput(BaseModel):
    destination: str
    netmask: str
    gateway: str
    interface: str
    metric: int

class RouteTableOutput(BaseModel):
    routes: list[RouteEntryOutput]