"""Tests de integración para el repositorio SQLite de IPAM."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.repositories.ipam_repository import SQLiteIpamRepository


@pytest.fixture
def repo():
    return SQLiteIpamRepository(db_path=":memory:")


def test_crear_y_listar(repo: SQLiteIpamRepository):
    nuevo = {
        "ip_address": "192.168.1.50",
        "status": "assigned",
        "assigned_to": "Servidor",
        "notes": "Crítico",
        "id": None
    }
    creado = repo.create(nuevo)
    assert creado["id"] == 1

    todos = repo.list_all()
    assert len(todos) == 1
    assert todos[0]["ip_address"] == "192.168.1.50"


def test_error_ip_duplicada(repo: SQLiteIpamRepository):
    ip = {
        "ip_address": "10.0.0.1",
        "status": "available",
        "assigned_to": "",
        "notes": "",
        "id": None
    }
    repo.create(ip)

    # Intentar crear la misma IP debe lanzar DomainError
    with pytest.raises(DomainError) as exc:
        repo.create(ip)
    
    assert exc.value.code == "duplicate_ip"