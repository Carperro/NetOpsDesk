from fastapi.testclient import TestClient

from netops_desk.api.main import app


client = TestClient(app)
ENDPOINT = "/api/v1/tools/vlsm/calculate"


def test_api_vlsm_happy_path():
    response = client.post(
        ENDPOINT,
        json={
            "network_cidr": "192.168.1.0/24",
            "requirements": [{"name": "Ventas", "hosts": 100}],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["base_network"] == "192.168.1.0/24"
    assert isinstance(data["allocated"], list)
    assert isinstance(data["remaining"], list)
    assert data["allocated"][0]["name"] == "Ventas"


def test_api_vlsm_error_dominio():
    response = client.post(
        ENDPOINT,
        json={
            "network_cidr": "192.168.1.0/24",
            "requirements": [{"name": "Ventas", "hosts": 500}],
        },
    )

    assert response.status_code == 400
    assert "demasiado grande" in response.json()["detail"]


def test_api_vlsm_validacion_pydantic():
    response = client.post(
        ENDPOINT,
        json={
            "network_cidr": "192.168.1.0/24",
            "requirements": [{"name": "Ventas", "hosts": 0}],
        },
    )

    assert response.status_code == 422
    assert response.status_code != 500


def test_api_vlsm_nombre_vacio():
    response = client.post(
        ENDPOINT,
        json={
            "network_cidr": "192.168.1.0/24",
            "requirements": [{"name": "", "hosts": 10}],
        },
    )

    assert response.status_code == 422
