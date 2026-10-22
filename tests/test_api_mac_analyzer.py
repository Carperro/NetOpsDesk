"""Tests de contrato HTTP para el Analizador MAC."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app
from netops_desk.api.routes.mac_analyzer import get_mac_runner

ENDPOINT = "/api/v1/tools/mac-analyzer/execute"

class FakeRunner:
    def lookup(self, mac: str) -> str:
        if mac == "00:1a:2b:3c:4d:5e":
            return "Cisco Systems, Inc"
        return "Desconocido"

def test_mac_valida_con_vendor(client: TestClient):
    res = client.post(ENDPOINT, json={"mac": "00-1A-2B-3C-4D-5E"}) # Con guiones para probar normalización
    assert res.status_code == 200
    data = res.json()
    assert data["mac_normalized"] == "00:1a:2b:3c:4d:5e"
    assert data["vendor"] == "Cisco Systems, Inc"

def test_mac_valida_sin_vendor(client: TestClient):
    res = client.post(ENDPOINT, json={"mac": "AA:BB:CC:DD:EE:FF"})
    assert res.status_code == 200
    assert res.json()["vendor"] == "Desconocido"

def test_mac_invalida(client: TestClient):
    res = client.post(ENDPOINT, json={"mac": "00:1A:2B:3C:4D"}) # Faltan octetos
    assert res.status_code == 422
    assert res.json()["error"] == "invalid_mac"
