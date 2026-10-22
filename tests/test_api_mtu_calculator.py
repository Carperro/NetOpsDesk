"""Tests de contrato HTTP para la Calculadora MTU."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app

ENDPOINT = "/api/v1/tools/mtu-calculator/calculate"

def test_mtu_exitoso_ipv4_tcp(client: TestClient):
    payload = {
        "mtu": 1500,
        "ip_version": "ipv4",
        "transport": "tcp",
        "tunnel": "none"
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["mss"] == 1460
    assert data["ip_header_size"] == 20

def test_mtu_valores_invalidos(client: TestClient):
    # MTU menor al mínimo (68)
    payload = {
        "mtu": 50,
        "ip_version": "ipv4",
        "transport": "tcp",
        "tunnel": "none"
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 422
    assert res.json()["error"] == "invalid_value" # Validación de Pydantic

def test_mtu_parametro_invalido(client: TestClient):
    # Túnel inventado
    payload = {
        "mtu": 1500,
        "ip_version": "ipv4",
        "transport": "tcp",
        "tunnel": "vpn-magica"
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 422
    assert res.json()["error"] == "invalid_parameter" # Validación de dominio
