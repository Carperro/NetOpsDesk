"""Tests de contrato HTTP para el Comparador de Configuraciones."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app

ENDPOINT = "/api/v1/tools/config-comparator/compare"

def test_comparacion_exitosa(client: TestClient):
    payload = {
        "config_a": "hostname Router1\nip 192.168.1.1",
        "config_b": "hostname Router1\nip 192.168.1.2"
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["has_changes"] is True
    assert len(data["diff_lines"]) > 0

def test_comparacion_sin_cambios(client: TestClient):
    payload = {
        "config_a": "hostname Router1",
        "config_b": "hostname Router1"
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["has_changes"] is False
    assert data["diff_lines"] == []

def test_comparacion_vacia(client: TestClient):
    payload = {
        "config_a": "   ",
        "config_b": ""
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 422
    assert res.json()["error"] == "empty_configs"
