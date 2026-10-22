"""Modelos de API para la calculadora IPv6/CIDR."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


__all__ = [
    "IPv6Input",
    "IPv6Output",
    "IPv6Warning",
]


class IPv6Input(BaseModel):
    """Cuerpo de entrada del cálculo IPv6.

    Solo admite el campo 'cidr'. Cualquier campo adicional es rechazado
    con HTTP 422 unknown_field (extra='forbid').
    """

    model_config = ConfigDict(extra="forbid")

    cidr: str = Field(
        ...,
        description="Dirección IPv6 con prefijo, ej: '2001:db8::/64'",
    )


class IPv6Warning(BaseModel):
    """Advertencia con código estable y mensaje legible."""

    code: str
    message: str


class IPv6Output(BaseModel):
    """Respuesta del cálculo IPv6.

    total_addresses es string decimal porque 2^128 excede
    Number.MAX_SAFE_INTEGER de JavaScript.
    """

    input: str
    address: str
    prefix_length: int
    network: str
    last_address: str
    total_addresses: str
    host_bits_set: bool
    classifications: list[str]
    warnings: list[IPv6Warning]