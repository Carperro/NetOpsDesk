"""Lógica de dominio para el Comparador de Configuraciones."""

from __future__ import annotations
import difflib
from typing import TypedDict
from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "ConfigDiffResult", "compare_configs"]

class ErrorCode:
    EMPTY_CONFIGS = "empty_configs"

class ConfigDiffResult(TypedDict):
    has_changes: bool
    diff_lines: list[str]

def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)

def compare_configs(*, config_a: str, config_b: str) -> ConfigDiffResult:
    """Compara dos textos y devuelve las diferencias."""
    text_a = config_a.strip()
    text_b = config_b.strip()

    if not text_a and not text_b:
        raise _error(
            ErrorCode.EMPTY_CONFIGS,
            "Al menos una de las configuraciones debe tener contenido."
        )

    # Si son iguales, ahorramos el procesamiento
    if text_a == text_b:
        return {"has_changes": False, "diff_lines": []}

    lines_a = text_a.splitlines()
    lines_b = text_b.splitlines()

    # lineterm="" evita que las líneas incluyan "\n" al final
    diff_generator = difflib.unified_diff(
        lines_a,
        lines_b,
        fromfile="Config A",
        tofile="Config B",
        lineterm=""
    )

    diff_lines = list(diff_generator)

    return {
        "has_changes": True,
        "diff_lines": diff_lines
    }