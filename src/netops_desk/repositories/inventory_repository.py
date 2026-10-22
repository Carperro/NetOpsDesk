"""Repositorio para el Inventario de Dispositivos (Persistencia SQLite)."""

from __future__ import annotations

from typing import Protocol, TypedDict

from netops_desk.repositories.sqlite_support import (
    connect_sqlite,
    translate_sqlite_operational_errors,
)


class Device(TypedDict):
    id: int | None
    name: str
    ip_address: str
    device_type: str
    location: str
    notes: str


class InventoryRepository(Protocol):
    """Interfaz para la persistencia de dispositivos."""
    def create(self, device: Device) -> Device: ...
    def list_all(self) -> list[Device]: ...
    def update(self, device_id: int, device: Device) -> Device: ...
    def delete(self, device_id: int) -> bool: ...
    def get_by_id(self, device_id: int) -> Device | None: ...


class SQLiteInventoryRepository:
    """Implementación real usando SQLite."""

    @translate_sqlite_operational_errors
    def __init__(self, db_path: str = "netops.db"):
        self.db_path = db_path
        # Mantenemos UNA SOLA conexión viva durante toda la vida del objeto.
        # check_same_thread=False es necesario para FastAPI (que usa threadpool).
        self._conn = connect_sqlite(self.db_path)
        self._create_table()

    def _create_table(self) -> None:
        # El bloque "with self._conn" hace un commit automático al salir.
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    location TEXT,
                    notes TEXT
                )
            """)

    @translate_sqlite_operational_errors
    def create(self, device: Device) -> Device:
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute(
                "INSERT INTO devices (name, ip_address, device_type, location, notes) VALUES (?, ?, ?, ?, ?)",
                (device["name"], device["ip_address"], device["device_type"], device["location"], device["notes"])
            )
            device["id"] = cursor.lastrowid
            return device

    @translate_sqlite_operational_errors
    def list_all(self) -> list[Device]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM devices ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

    @translate_sqlite_operational_errors
    def get_by_id(self, device_id: int) -> Device | None:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @translate_sqlite_operational_errors
    def update(self, device_id: int, device: Device) -> Device:
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute(
                "UPDATE devices SET name=?, ip_address=?, device_type=?, location=?, notes=? WHERE id=?",
                (device["name"], device["ip_address"], device["device_type"], device["location"], device["notes"], device_id)
            )
            device["id"] = device_id
            return device

    @translate_sqlite_operational_errors
    def delete(self, device_id: int) -> bool:
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
            return cursor.rowcount > 0
