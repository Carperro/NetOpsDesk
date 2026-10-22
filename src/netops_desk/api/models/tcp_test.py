"""Modelos de API para la Prueba de puertos TCP."""

from pydantic import BaseModel, ConfigDict, Field


class TcpTestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str = Field(..., description="IPv4, IPv6 o hostname")
    port: int = Field(..., ge=1, le=65535, description="Puerto TCP (1-65535)")
    timeout_ms: int = Field(default=3000, ge=500, le=10000, description="Timeout en ms (500-10000)")


class TcpTestOutput(BaseModel):
    host: str
    port: int
    status: str
    time_ms: float