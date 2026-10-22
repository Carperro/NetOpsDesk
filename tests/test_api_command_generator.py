"""Tests de contrato HTTP para el Generador de Comandos."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app

ENDPOINT = "/api/v1/tools/command-generator/generate"

def test_generar_ping(client: TestClient):
    payload = {
        "command_type": "ping",
        "target": "8.8.8.8",
        "options": ["-t"]
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["command"] == "ping -t 8.8.8.8"
    assert data["requires_admin"] is False

def test_generar_ipconfig_admin(client: TestClient):
    payload = {
        "command_type": "ipconfig",
        "options": ["/flushdns"]
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["command"] == "ipconfig /flushdns"
    assert data["requires_admin"] is True

def test_error_falta_target(client: TestClient):
    payload = {
        "command_type": "ping",
        "options": []
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 422
    assert res.json()["error"] == "missing_target"

def test_error_opcion_invalida(client: TestClient):
    payload = {
        "command_type": "ping",
        "target": "8.8.8.8",
        "options": ["-hack"]
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 422
    assert res.json()["error"] == "invalid_option"
