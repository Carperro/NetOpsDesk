"""Modelos de API para el Asistente de Resolución."""

from pydantic import BaseModel

class CauseOutput(BaseModel):
    cause: str
    steps: list[str]

class SymptomOutput(BaseModel):
    symptom_id: str
    symptom_name: str
    causes: list[CauseOutput]