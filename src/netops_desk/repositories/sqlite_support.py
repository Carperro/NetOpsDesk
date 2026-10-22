"""Utilidades compartidas para conexiones SQLite de los repositorios."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from functools import wraps

from netops_desk.exceptions import DomainError


def _db_locked(error: sqlite3.OperationalError) -> DomainError:
    return DomainError(
        message="La base de datos está bloqueada o no está disponible.",
        code="db_locked",
    )


def connect_sqlite(db_path: str) -> sqlite3.Connection:
    """Abre SQLite con espera acotada y WAL cuando el backend lo admite."""
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=5000;")
        connection.execute("PRAGMA journal_mode=WAL;")
        return connection
    except sqlite3.OperationalError as exc:
        if connection is not None:
            connection.close()
        raise _db_locked(exc) from exc


def translate_sqlite_operational_errors[**P, R](
    operation: Callable[P, R],
) -> Callable[P, R]:
    """Traduce errores operativos SQLite al error de dominio común."""

    @wraps(operation)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return operation(*args, **kwargs)
        except sqlite3.OperationalError as exc:
            raise _db_locked(exc) from exc

    return wrapped
