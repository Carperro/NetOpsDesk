"""Tests unitarios y de contrato para el Catálogo de Puertos."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app
from netops_desk.port_catalog import search_ports

ENDPOINT = "/api/v1/tools/port-catalog/search"

# --- Tests de Dominio ---

def test_busqueda_vacia_devuelve_todo():
    res = search_ports("")
    assert len(res) >= 20

def test_busqueda_por_puerto():
    res = search_ports("80")
    # Debería traer el 80 y el 8080
    assert len(res) == 2
    assert any(r["service"] == "HTTP" for r in res)

def test_busqueda_por_servicio():
    res = search_ports("ssh")
    assert len(res) == 1
    assert res[0]["port"] == 22

def test_busqueda_sin_resultados():
    res = search_ports("puerto-inventado")
    assert res == []

# --- Tests de API ---

def test_api_busqueda_exitosa(client: TestClient):
    res = client.get(f"{ENDPOINT}?query=http")
    assert res.status_code == 200
    data = res.json()
    # "http" debería matchear HTTP, HTTPS y HTTP-Alt
    assert len(data["ports"]) >= 2

def test_api_sin_query(client: TestClient):
    res = client.get(ENDPOINT)
    assert res.status_code == 200
    assert len(res.json()["ports"]) >= 20
