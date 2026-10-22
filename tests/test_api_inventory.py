"""Tests de contrato HTTP para el Inventario de Dispositivos."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app
from netops_desk.api.routes.inventory import get_inventory_repo
from netops_desk.repositories.inventory_repository import SQLiteInventoryRepository

ENDPOINT = "/api/v1/tools/inventory/devices"

def test_crud_inventario(client: TestClient):
    # 1. Listar (vacío al principio)
    res = client.get(ENDPOINT)
    assert res.status_code == 200
    assert res.json() == []

    # 2. Crear
    payload = {
        "name": "Router Test",
        "ip_address": "192.168.1.1",
        "device_type": "Router",
        "location": "Lab",
        "notes": "Test"
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == 1
    device_id = data["id"]

    # 3. Listar (ahora hay 1)
    res = client.get(ENDPOINT)
    assert len(res.json()) == 1

    # 4. Actualizar
    payload["name"] = "Router Core"
    res = client.put(f"{ENDPOINT}/{device_id}", json=payload)
    assert res.status_code == 200
    assert res.json()["name"] == "Router Core"

    # 5. Eliminar
    res = client.delete(f"{ENDPOINT}/{device_id}")
    assert res.status_code == 204

    # 6. Listar (vacío de nuevo)
    res = client.get(ENDPOINT)
    assert len(res.json()) == 0

def test_crear_dispositivo_invalido(client: TestClient):
    payload = {"name": "Router", "ip_address": "999.999.999.999"}
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 422
    assert res.json()["error"] == "invalid_ip"

def test_actualizar_inexistente(client: TestClient):
    payload = {"name": "Ghost", "ip_address": "1.1.1.1"}
    res = client.put(f"{ENDPOINT}/99", json=payload)
    assert res.status_code == 422
    assert res.json()["error"] == "not_found"
