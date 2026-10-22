"""Modelos de API para el Generador de Informes."""

from pydantic import BaseModel, ConfigDict, Field

class FindingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    step: str = Field(..., description="Paso del diagnóstico")
    result: str = Field(..., description="Resultado del paso")

class ReportGeneratorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(..., description="Título del informe")
    author: str | None = Field(default=None, description="Nombre del técnico")
    date: str | None = Field(default=None, description="Fecha del informe (default: hoy)")
    findings: list[FindingInput] = Field(..., description="Lista de hallazgos")
    conclusion: str | None = Field(default=None, description="Conclusión final")

class ReportGeneratorOutput(BaseModel):
    report_markdown: str