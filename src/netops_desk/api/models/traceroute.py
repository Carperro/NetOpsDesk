"""Modelos de API para la herramienta Traceroute."""

from pydantic import BaseModel, ConfigDict, Field


class TracerouteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str = Field(..., description="IPv4, IPv6 o hostname")
    max_hops: int = Field(default=15, ge=1, le=30, description="Máximo de saltos (1-30)")


class TracerouteHopOutput(BaseModel):
    hop_number: int
    ip: str | None
    times_ms: list[float]


class TracerouteOutput(BaseModel):
    host: str
    resolved_ip: str
    hops: list[TracerouteHopOutput]