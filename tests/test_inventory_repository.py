"""Tests de integración para el repositorio SQLite (en memoria)."""

import pytest
from netops_desk.repositories.inventory_repository import SQLiteInventoryRepository


@pytest.fixture
def repo():
    # Usar :memory: hace que la base de datos viva en la RAM y se destruya al terminar el test
    return SQLiteInventoryRepository(db_path=":memory:")


def test_crear_y_listar_dispositivo(repo: SQLiteInventoryRepository):
    nuevo = {
        "name": "Router Principal",
        "ip_address": "192.168.1.1",
        "device_type": "Router",
        "location": "Rack A",
        "notes": "Mikrotik",
        "id": None
    }
    
    creado = repo.create(nuevo)
    assert creado["id"] == 1
    
    todos = repo.list_all()
    assert len(todos) == 1
    assert todos[0]["name"] == "Router Principal"


def test_actualizar_dispositivo(repo: SQLiteInventoryRepository):
    creado = repo.create({"name": "Switch", "ip_address": "10.0.0.2", "device_type": "Switch", "location": "Piso 1", "notes": "", "id": None})
    
    actualizado = repo.update(
        device_id=creado["id"],
        device={"name": "Switch Core", "ip_address": "10.0.0.2", "device_type": "Switch", "location": "Piso 2", "notes": "Actualizado", "id": None}
    )
    
    assert actualizado["name"] == "Switch Core"
    assert repo.get_by_id(creado["id"])["location"] == "Piso 2"


def test_eliminar_dispositivo(repo: SQLiteInventoryRepository):
    creado = repo.create({"name": "PC", "ip_address": "10.0.0.3", "device_type": "PC", "location": "Oficina", "notes": "", "id": None})
    
    eliminado = repo.delete(creado["id"])
    assert eliminado is True
    assert repo.get_by_id(creado["id"]) is None

    no_eliminado = repo.delete(999) # ID que no existe
    assert no_eliminado is False