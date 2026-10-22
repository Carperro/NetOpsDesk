"""Repositorio para el Historial de Diagnósticos (SQLite)."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, TypedDict

from netops_desk.repositories.sqlite_support import (
    connect_sqlite,
    translate_sqlite_operational_errors,
)


class HistoryRecord(TypedDict):
    id: int | None
    tool_name: str
    action: str
    result_status: str
    details: str
    created_at: str | None


class HistoryRepository(Protocol):
    def create(self, record: HistoryRecord) -> HistoryRecord: ...
    def list_all(self) -> list[HistoryRecord]: ...
    def delete(self, record_id: int) -> bool: ...
    def clear_all(self) -> None: ...


class SQLiteHistoryRepository:
    @translate_sqlite_operational_errors
    def __init__(self, db_path: str = "netops.db"):
        self.db_path = db_path
        self._conn = connect_sqlite(self.db_path)
        self._create_table()

    def _create_table(self) -> None:
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    result_status TEXT NOT NULL,
                    details TEXT,
                    created_at TEXT NOT NULL
                )
            """)

    @translate_sqlite_operational_errors
    def create(self, record: HistoryRecord) -> HistoryRecord:
        record["created_at"] = datetime.now().isoformat()
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute(
                "INSERT INTO history (tool_name, action, result_status, details, created_at) VALUES (?, ?, ?, ?, ?)",
                (record["tool_name"], record["action"], record["result_status"], record["details"], record["created_at"])
            )
            record["id"] = cursor.lastrowid
            return record

    @translate_sqlite_operational_errors
    def list_all(self) -> list[HistoryRecord]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM history ORDER BY created_at DESC, id DESC")
        return [dict(row) for row in cursor.fetchall()]

    @translate_sqlite_operational_errors
    def delete(self, record_id: int) -> bool:
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM history WHERE id = ?", (record_id,))
            return cursor.rowcount > 0

    @translate_sqlite_operational_errors
    def clear_all(self) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM history")
