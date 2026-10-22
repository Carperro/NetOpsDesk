from typing import TypedDict

from pwdlib import PasswordHash

from netops_desk.repositories.sqlite_support import (
    connect_sqlite,
    translate_sqlite_operational_errors,
)

# Usamos la recomendación actual de OWASP: Argon2
password_hash = PasswordHash.recommended()

class User(TypedDict):
    id: int | None
    username: str
    password_hash: str
    role: str

class SQLiteUserRepository:
    @translate_sqlite_operational_errors
    def __init__(self, db_path: str = "netops.db"):
        self.db_path = db_path
        self._conn = connect_sqlite(self.db_path)
        self._create_table()
        self._create_default_admin()

    def _create_table(self) -> None:
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """)

    def _create_default_admin(self) -> None:
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                hashed_pw = password_hash.hash("admin")
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    ("admin", hashed_pw, "admin")
                )

    @translate_sqlite_operational_errors
    def get_by_username(self, username: str) -> User | None:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
