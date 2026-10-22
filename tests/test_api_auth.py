"""Tests de contrato HTTP para Autenticación."""

import pytest
from fastapi.testclient import TestClient
from netops_desk.api.main import create_app
from netops_desk.api.routes.auth import get_user_repo
from netops_desk.repositories.user_repository import SQLiteUserRepository

ENDPOINT = "/api/v1/auth/login"

@pytest.fixture
def client():
    app = create_app()
    # Usamos una DB en memoria para el usuario
    test_repo = SQLiteUserRepository(db_path=":memory:")
    app.dependency_overrides[get_user_repo] = lambda: test_repo
    return TestClient(app)

def test_login_exitoso(client: TestClient):
    # Usamos el admin/admin que crea automáticamente el repositorio
    res = client.post(ENDPOINT, json={"username": "admin", "password": "admin"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_login_credenciales_invalidas(client: TestClient):
    res = client.post(ENDPOINT, json={"username": "admin", "password": "mal"})
    assert res.status_code == 401
    assert res.json()["error"] == "invalid_credentials"
    assert res.json()["detail"] == "Usuario o contraseña incorrectos."


def test_rutas_de_herramientas_requieren_token(client: TestClient):
    res = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24"},
    )

    assert res.status_code == 401
    assert res.json()["error"] == "unauthorized"


def test_token_de_login_autoriza_ruta_de_herramienta(client: TestClient):
    login = client.post(ENDPOINT, json={"username": "admin", "password": "admin"})
    assert login.status_code == 200

    res = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24"},
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert res.status_code == 200
