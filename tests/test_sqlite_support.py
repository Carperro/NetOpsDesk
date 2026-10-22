import sqlite3

import pytest

from netops_desk.exceptions import DomainError
from netops_desk.repositories.inventory_repository import SQLiteInventoryRepository
from netops_desk.repositories.sqlite_support import connect_sqlite


def test_connection_uses_wal_and_busy_timeout(tmp_path):
    connection = connect_sqlite(str(tmp_path / "netops.sqlite3"))
    try:
        assert connection.execute("PRAGMA journal_mode;").fetchone()[0].lower() == "wal"
        assert connection.execute("PRAGMA busy_timeout;").fetchone()[0] == 5000
    finally:
        connection.close()


def test_repository_translates_locked_database_to_domain_error(tmp_path):
    db_path = str(tmp_path / "netops.sqlite3")
    repository = SQLiteInventoryRepository(db_path=db_path)
    blocker = sqlite3.connect(db_path, timeout=0, isolation_level=None)
    blocker.execute("BEGIN IMMEDIATE")
    repository._conn.execute("PRAGMA busy_timeout=25;")
    device = {
        "id": None,
        "name": "Router",
        "ip_address": "192.0.2.1",
        "device_type": "Router",
        "location": "Lab",
        "notes": "",
    }

    try:
        with pytest.raises(DomainError) as exc:
            repository.create(device)
        assert exc.value.code == "db_locked"
    finally:
        blocker.rollback()
        blocker.close()
        repository._conn.close()
