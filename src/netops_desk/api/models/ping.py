"""Modelos de API para la herramienta Ping."""

from pydantic import BaseModel, ConfigDict, Field


class PingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str = Field(..., description="IPv4, IPv6 o hostname")
    count: int = Field(default=4, ge=1, le=10, description="Cantidad de paquetes (1-10)")


class PingResponseItem(BaseModel):
    seq: int
    time_ms: float


class PingOutput(BaseModel):
    host: str
    resolved_ip: str
    packets_sent: int
    packets_received: int
    packet_loss_percent: float
    min_ms: float | None
    max_ms: float | None
    avg_ms: float | None
    responses: list[PingResponseItem]