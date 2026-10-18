import pytest
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

    assert response.status_code == 422
    assert set(response.json()) == {"error", "detail"}
    assert response.json()["error"]
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


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"network_cidr": "192.168.1.0/24", "requirements": []},
        {"network_cidr": "192.168.1.0/24", "requirements": [{"name": "Ventas"}]},
        {"network_cidr": "192.168.1.0/24", "requirements": [{"name": "Ventas", "hosts": "diez"}]},
    ],
)
def test_api_vlsm_rechaza_solicitudes_incompletas_o_mal_tipadas(payload):
    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422
    assert set(response.json()) == {"error", "detail"}
    assert response.json()["error"]
    assert response.json()["detail"]


def test_api_vlsm_respuesta_contiene_el_esquema_completo():
    response = client.post(
        ENDPOINT,
        json={
            "network_cidr": "192.0.2.0/29",
            "requirements": [{"name": "LAN", "hosts": 2}],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"base_network", "allocated", "remaining"}
    assert set(data["allocated"][0]) == {
        "name", "network", "prefix", "netmask", "broadcast", "first_host",
        "last_host", "total_ips", "hosts_needed",
    }
    assert data["remaining"] == [
        {"network": "192.0.2.4", "broadcast": "192.0.2.7", "total_ips": 4}
    ]


def test_api_vlsm_rechaza_tipo_de_contenido_no_admitido():
    response = client.post(
        ENDPOINT,
        content='{"network_cidr":"192.0.2.0/24","requirements":[{"name":"LAN","hosts":2}]}',
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 415
    assert set(response.json()) == {"error", "detail"}
