"""Tests de contrato HTTP para Asistente de Configuración IP."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app

ENDPOINT = "/api/v1/tools/ip-config/execute"

def test_generar_comando_static(client: TestClient):
    payload = {
        "action": "set_static",
        "interface_name": "Wi-Fi",
        "ip": "192.168.1.100",
        "mask": "255.255.255.0",
        "gateway": "192.168.1.1"
    }
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 'static 192.168.1.100 255.255.255.0 192.168.1.1' in data["command"]

def test_generar_comando_renew(client: TestClient):
    payload = {"action": "renew_dhcp", "interface_name": "Ethernet"}
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 200
    assert 'ipconfig /renew "Ethernet"' == response.json()["command"]

def test_error_interface_invalida(client: TestClient):
    payload = {"action": "renew_dhcp", "interface_name": 'Wi-Fi"; rm -rf /'}
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_interface_name"

def test_error_faltan_campos_static(client: TestClient):
    payload = {"action": "set_static", "interface_name": "Wi-Fi", "ip": "192.168.1.100"}
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "missing_fields"
