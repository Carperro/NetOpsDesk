"""Repositorio para el Gestor de Direcciones IP (IPAM)."""

from __future__ import annotations

import sqlite3
from typing import Protocol, TypedDict

from netops_desk.exceptions import DomainError
from netops_desk.repositories.sqlite_support import (
    connect_sqlite,
    translate_sqlite_operational_errors,
)


class IpamRecord(TypedDict):
    id: int | None
    ip_address: str
    status: str
    assigned_to: str
    notes: str


class IpamRepository(Protocol):
    """Interfaz para la persistencia de IPAM."""
    def create(self, record: IpamRecord) -> IpamRecord: ...
    def list_all(self) -> list[IpamRecord]: ...
    def update(self, record_id: int, record: IpamRecord) -> IpamRecord: ...
    def delete(self, record_id: int) -> bool: ...
    def get_by_id(self, record_id: int) -> IpamRecord | None: ...


class SQLiteIpamRepository:
    """Implementación real usando SQLite."""

    @translate_sqlite_operational_errors
    def __init__(self, db_path: str = "netops.db"):
        self.db_path = db_path
        self._conn = connect_sqlite(self.db_path)
        self._create_table()

    def _create_table(self) -> None:
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS ip_addresses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    assigned_to TEXT,
                    notes TEXT
                )
            """)

    @translate_sqlite_operational_errors
    def create(self, record: IpamRecord) -> IpamRecord:
        try:
            with self._conn:
                cursor = self._conn.cursor()
                cursor.execute(
                    "INSERT INTO ip_addresses (ip_address, status, assigned_to, notes) VALUES (?, ?, ?, ?)",
                    (record["ip_address"], record["status"], record["assigned_to"], record["notes"])
                )
                record["id"] = cursor.lastrowid
                return record
        except sqlite3.IntegrityError as exc:
            # Capturamos la violación del UNIQUE y la traducimos a error de dominio
            if "UNIQUE constraint failed" in str(exc):
                raise DomainError(message="La dirección IP ya está registrada.", code="duplicate_ip") from exc
            raise exc

    @translate_sqlite_operational_errors
    def list_all(self) -> list[IpamRecord]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM ip_addresses ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

    @translate_sqlite_operational_errors
    def get_by_id(self, record_id: int) -> IpamRecord | None:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM ip_addresses WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @translate_sqlite_operational_errors
    def update(self, record_id: int, record: IpamRecord) -> IpamRecord:
        try:
            with self._conn:
                cursor = self._conn.cursor()
                cursor.execute(
                    "UPDATE ip_addresses SET ip_address=?, status=?, assigned_to=?, notes=? WHERE id=?",
                    (record["ip_address"], record["status"], record["assigned_to"], record["notes"], record_id)
                )
                record["id"] = record_id
                return record
        except sqlite3.IntegrityError as exc:
            if "UNIQUE constraint failed" in str(exc):
                raise DomainError(message="La dirección IP ya está registrada.", code="duplicate_ip") from exc
            raise exc

    @translate_sqlite_operational_errors
    def delete(self, record_id: int) -> bool:
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM ip_addresses WHERE id = ?", (record_id,))
            return cursor.rowcount > 0
