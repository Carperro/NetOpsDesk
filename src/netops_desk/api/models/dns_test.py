"""Modelos de API para Diagnóstico DNS."""

from pydantic import BaseModel, ConfigDict, Field


class DnsTestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: str = Field(..., description="Dominio a consultar (ej. google.com)")
    record_type: str = Field(..., description="A, AAAA, MX, TXT, NS o CNAME")
    resolver: str | None = Field(default=None, description="IP del DNS (ej. 8.8.8.8). Si es null, usa el del sistema.")


class DnsTestOutput(BaseModel):
    domain: str
    record_type: str
    resolver: str
    status: str
    time_ms: float
    records: list[str]