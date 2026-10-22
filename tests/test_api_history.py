"""Tests de contrato HTTP para el Historial."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app
from netops_desk.api.routes.history import get_history_repo
from netops_desk.repositories.history_repository import SQLiteHistoryRepository

ENDPOINT = "/api/v1/tools/history/logs"

def test_historial_flujo_completo(client: TestClient):
    # 1. Crear
    payload = {"tool_name": "ping", "action": "Test", "result_status": "success", "details": "OK"}
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 201
    log_id = res.json()["id"]

    # 2. Listar
    res = client.get(ENDPOINT)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # 3. Borrar uno
    res = client.delete(f"{ENDPOINT}/{log_id}")
    assert res.status_code == 204

    # 4. Borrar todo
    client.post(ENDPOINT, json=payload)
    res = client.delete(ENDPOINT)
    assert res.status_code == 204
    assert len(client.get(ENDPOINT).json()) == 0
