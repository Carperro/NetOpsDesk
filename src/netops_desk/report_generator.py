"""Lógica de dominio para el Generador de Informes de Diagnóstico."""

from __future__ import annotations
from datetime import date
from typing import TypedDict
from netops_desk.exceptions import DomainError

__all__ = ["DomainError", "ErrorCode", "ReportInput", "generate_report"]

class ErrorCode:
    MISSING_TITLE = "missing_title"
    EMPTY_FINDINGS = "empty_findings"
    MISSING_FINDING_FIELDS = "missing_finding_fields"

class Finding(TypedDict):
    step: str
    result: str

class ReportInput(TypedDict):
    title: str
    author: str | None
    date: str | None
    findings: list[Finding]
    conclusion: str | None

def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)

def generate_report(*, data: ReportInput) -> str:
    """Genera el reporte en formato Markdown."""
    title = (data.get("title") or "").strip()
    if not title:
        raise _error(ErrorCode.MISSING_TITLE, "El título del informe es obligatorio.")
    
    findings = data.get("findings", [])
    if not findings:
        raise _error(ErrorCode.EMPTY_FINDINGS, "El informe debe contener al menos un hallazgo.")

    for f in findings:
        if not (f.get("step") or "").strip() or not (f.get("result") or "").strip():
            raise _error(ErrorCode.MISSING_FINDING_FIELDS, "Cada hallazgo debe tener un 'step' y un 'result'.")

    author = (data.get("author") or "").strip() or "Anónimo"
    
    fecha = data.get("date")
    if not fecha:
        fecha = date.today().isoformat()
        
    conclusion = (data.get("conclusion") or "").strip()

    md_lines = [
        f"# {title}",
        "",
        f"**Técnico:** {author}",
        f"**Fecha:** {fecha}",
        "",
        "## Hallazgos",
        ""
    ]

    for f in findings:
        md_lines.append(f"### {(f.get('step') or '').strip()}")
        md_lines.append(f"{(f.get('result') or '').strip()}")
        md_lines.append("")

    if conclusion:
        md_lines.append("## Conclusión")
        md_lines.append(conclusion)
        md_lines.append("")

    return "\n".join(md_lines).strip()