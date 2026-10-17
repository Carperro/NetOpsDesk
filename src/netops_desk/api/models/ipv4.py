"""Modelos Pydantic para la API IPv4/CIDR de NetOps Desk.

Estos modelos definen el contrato de entrada y salida de la API. No
contienen lógica de negocio: solo validación estructural y de tipos.

El modelo de entrada usa 'object' en los campos que admiten varias formas
(cadena, IPv4Address), y toda la validación se centraliza en un único
'model_validator' para respetar el orden del contrato:

    1. Presencia y exclusión mutua de formas.
    2. Campos faltantes.
    3. Tipos y valores individuales.
"""

from __future__ import annotations

from ipaddress import IPv4Address
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

class IPV4Input(BaseModel):
    """Entrada unificada para cálculo directo o inverso.

    Detecta automáticamente qué operación se quiere ejecutar según los
    campos presentes:
    - Cálculo directo: 'cidr' o ('address' + 'netmask').
    - Cálculo inverso: 'required_hosts' (+ 'mode' obligatorio).

    Los campos de una y otra forma son mutuamente excluyentes.
    """

    model_config = ConfigDict(extra="forbid")

    cidr: object | None = Field(
        default=None,
        description="Dirección IPv4 con prefijo, ej: '192.168.1.0/24'.",
    )
    address: object | None = Field(
        default=None,
        description="Dirección IPv4, ej: '192.168.1.0'.",
    )
    netmask: object | None = Field(
        default=None,
        description="Máscara de subred, ej: '255.255.255.0'.",
    )
    required_hosts: int | None = Field(
        default=None,
        gt=0,
        strict=True,
        description="Cantidad de hosts usables requeridos (para cálculo inverso).",
    )
    mode: Literal["conventional", "point-to-point"] = Field(
        default="conventional",
        description="Modo de cálculo a aplicar.",
    )

    @model_validator(mode="after")
    def _validar_operacion(self) -> "IPV4Input":
        """Valida la operación completa en el orden del contrato."""
        tiene_cidr = self.cidr is not None
        tiene_direccion = self.address is not None
        tiene_mascara = self.netmask is not None
        tiene_hosts = self.required_hosts is not None
        tiene_directos = tiene_cidr or tiene_direccion or tiene_mascara

        # 1. Directo e inverso a la vez: incompatible.
        if tiene_directos and tiene_hosts:
            raise PydanticCustomError(
                "incompatible_inputs",
                "Los campos de cálculo directo y 'required_hosts' son mutuamente excluyentes.",
            )

        # 2. Ni una forma ni la otra.
        if not tiene_directos and not tiene_hosts:
            raise PydanticCustomError(
                "missing_field",
                "Debe proporcionar 'cidr', 'address'+'netmask' o 'required_hosts'.",
            )

        # 3. CIDR combinado con address o netmask.
        if tiene_cidr and (tiene_direccion or tiene_mascara):
            raise PydanticCustomError(
                "incompatible_inputs",
                "Los campos 'cidr' y 'address'/'netmask' son mutuamente excluyentes.",
            )

        # 4. Falta uno de los dos campos del par (solo si es cálculo directo).
        if not tiene_hosts and tiene_direccion != tiene_mascara:
            raise PydanticCustomError(
                "missing_field",
                "Los campos 'address' y 'netmask' deben proporcionarse juntos.",
            )

        # 5. Cálculo inverso: 'mode' es obligatorio.
        if tiene_hosts and "mode" not in self.model_fields_set:
            raise PydanticCustomError(
                "missing_field",
                "El campo 'mode' es obligatorio para el cálculo inverso.",
            )

        # 6. Validación de tipos y valores (solo después de la estructural).
        if tiene_cidr:
            self._validar_cidr()
        if tiene_direccion:
            self.address = self._validar_ipv4(self.address, "address")
        if tiene_mascara:
            self.netmask = self._validar_ipv4(self.netmask, "netmask")

        return self

    def _validar_cidr(self) -> None:
        """Valida que 'cidr' sea una cadena."""
        if not isinstance(self.cidr, str):
            raise PydanticCustomError(
                "invalid_type",
                "El campo 'cidr' debe ser una cadena.",
            )

    @staticmethod
    def _validar_ipv4(value: object, field: str) -> IPv4Address:
        """Valida y convierte un valor en una dirección IPv4."""
        if isinstance(value, IPv4Address):
            return value

        if isinstance(value, str):
            try:
                return IPv4Address(value)
            except ValueError as exc:
                raise PydanticCustomError(
                    "invalid_value",
                    f"El campo '{field}' debe ser una dirección IPv4 válida.",
                ) from exc

        raise PydanticCustomError(
            "invalid_type",
            f"El campo '{field}' debe ser una dirección IPv4 en formato string.",
        )

# ---------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------

class IPV4DirectOutput(BaseModel):
    """Resultado del cálculo directo."""

    model_config = ConfigDict(extra="forbid")

    network: IPv4Address = Field(description="Dirección de red.")
    broadcast: IPv4Address | None = Field(description="Dirección de broadcast.")
    netmask: IPv4Address = Field(description="Máscara de subred.")
    wildcard: IPv4Address = Field(description="Máscara wildcard.")
    first_usable: IPv4Address | None = Field(description="Primera dirección usable.")
    last_usable: IPv4Address | None = Field(description="Última dirección usable.")
    total_addresses: int = Field(description="Total de direcciones del bloque.")
    usable_addresses: int = Field(description="Cantidad de direcciones usables.")
    binary: dict[str, str | None] = Field(
        description="Representación binaria de los campos anteriores."
    )
    warnings: list[dict[str, str]] = Field(
        description="Advertencias emitidas durante el cálculo."
    )

class IPV4InverseOutput(BaseModel):
    """Resultado del cálculo inverso."""

    model_config = ConfigDict(extra="forbid")

    required_hosts: int = Field(description="Cantidad de hosts solicitada.")
    mode_requested: Literal["conventional", "point-to-point"] = Field(
        description="Modo solicitado por el cliente."
    )
    mode_applied: Literal["conventional", "point-to-point"] = Field(
        description="Modo efectivamente aplicado."
    )
    prefix: int = Field(description="Prefijo calculado (0-32).")
    total_addresses: int = Field(description="Total de direcciones del bloque.")
    usable_addresses: int = Field(description="Cantidad de direcciones usables.")
    warnings: list[dict[str, str]] = Field(
        description="Advertencias emitidas durante el cálculo."
    )

# ---------------------------------------------------------------------------
# Errores
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Respuesta de error uniforme para toda la API."""

    error: str = Field(description="Código de error estable del contrato.")
    detail: str = Field(description="Mensaje legible para el usuario.")