"""Tests de contrato HTTP para el Generador de Informes."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app

ENDPOINT = "/api/v1/tools/report-generator/generate"

def test_generar_reporte_exitoso(client: TestClient):
    payload = {
        "title": "Diagnóstico Oficina",
        "author": "Soporte IT",
        "findings": [
            {"step": "Ping al Gateway", "result": "Exitoso, 1ms"},
            {"step": "Prueba DNS", "result": "Falló"}
        ],
        "conclusion": "Revisar servidor DNS."
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "# Diagnóstico Oficina" in data["report_markdown"]
    assert "### Prueba DNS" in data["report_markdown"]

def test_generar_reporte_sin_titulo(client: TestClient):
    payload = {
        "title": "   ",
        "findings": [{"step": "A", "result": "B"}]
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 422
    assert res.json()["error"] == "missing_title"

def test_generar_reporte_sin_hallazgos(client: TestClient):
    payload = {
        "title": "Test",
        "findings": []
    }
    res = client.post(ENDPOINT, json=payload)
    assert res.status_code == 422
    assert res.json()["error"] == "empty_findings"
