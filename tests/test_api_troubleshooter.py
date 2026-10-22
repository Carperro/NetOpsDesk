"""Tests de contrato HTTP para el Asistente de Resolución."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app

ENDPOINT = "/api/v1/tools/troubleshooter/symptoms"

def test_sintoma_exitoso(client: TestClient):
    res = client.get(f"{ENDPOINT}/sin_internet")
    assert res.status_code == 200
    data = res.json()
    assert data["symptom_name"] == "Sin acceso a internet"
    assert len(data["causes"]) == 3

def test_sintoma_invalido(client: TestClient):
    res = client.get(f"{ENDPOINT}/sintoma_inventado")
    assert res.status_code == 422
    assert res.json()["error"] == "invalid_symptom"
