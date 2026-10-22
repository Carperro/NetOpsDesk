"""Lógica de dominio para el Historial de Diagnósticos."""

from __future__ import annotations
from typing import TypedDict
from netops_desk.exceptions import DomainError
from netops_desk.repositories.history_repository import HistoryRepository, HistoryRecord

__all__ = ["DomainError", "ErrorCode", "HistoryRecord", "add_log", "get_logs", "remove_log", "clear_logs"]


class ErrorCode:
    NOT_FOUND = "not_found"
    MISSING_FIELDS = "missing_fields"


def _error(code: str, message: str) -> DomainError:
    return DomainError(message=message, code=code)


def add_log(*, repo: HistoryRepository, data: dict) -> HistoryRecord:
    tool_name = data.get("tool_name", "").strip()
    action = data.get("action", "").strip()
    
    if not tool_name or not action:
        raise _error(ErrorCode.MISSING_FIELDS, "El nombre de la herramienta y la acción son obligatorios.")

    record: HistoryRecord = {
        "id": None,
        "tool_name": tool_name,
        "action": action,
        "result_status": data.get("result_status", "").strip() or "unknown",
        "details": data.get("details", "").strip(),
        "created_at": None
    }
    return repo.create(record)


def get_logs(*, repo: HistoryRepository) -> list[HistoryRecord]:
    return repo.list_all()


def remove_log(*, repo: HistoryRepository, record_id: int) -> bool:
    if not repo.delete(record_id):
        raise _error(ErrorCode.NOT_FOUND, "Entrada de historial no encontrada.")
    return True


def clear_logs(*, repo: HistoryRepository) -> None:
    repo.clear_all()