"""Tests de contrato HTTP para el Gestor de Direcciones IP (IPAM)."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app
from netops_desk.api.routes.ipam import get_ipam_repo
from netops_desk.repositories.ipam_repository import SQLiteIpamRepository

ENDPOINT = "/api/v1/tools/ipam/addresses"

def test_crud_ipam_completo(client: TestClient):
    # 1. Crear registro
    payload = {
        "ip_address": "192.168.1.50",
        "status": "assigned",
        "assigned_to": "Servidor de desarrollo",
        "notes": "No tocar"
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == 1
    record_id = data["id"]

    # 2. Intentar crear un duplicado (debe fallar por UNIQUE)
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 422
    assert res.json()["error"] == "duplicate_ip"

    # 3. Listar
    res = client.get(ENDPOINT)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # 4. Actualizar estado
    payload["status"] = "reserved"
    res = client.put(f"{ENDPOINT}/{record_id}", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "reserved"

    # 5. Eliminar
    res = client.delete(f"{ENDPOINT}/{record_id}")
    assert res.status_code == 204

    # 6. Verificar que ya no está
    res = client.get(ENDPOINT)
    assert len(res.json()) == 0


def test_crear_ip_invalida_api(client: TestClient):
    res = client.post(ENDPOINT, json={"ip_address": "1.2.3.4.5", "status": "available"})
    assert res.status_code == 422
    assert res.json()["error"] == "invalid_ip"
