import json

import pytest
from fastapi.testclient import TestClient

from netops_desk.api.main import app


client = TestClient(app)
BY_COUNT = "/api/v1/tools/subnetting/by-count"
BY_HOSTS = "/api/v1/tools/subnetting/by-hosts"


@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        (BY_COUNT, {"network_cidr": "192.0.2.0/24", "subnet_count": 2}),
        (BY_HOSTS, {"network_cidr": "192.0.2.0/24", "required_hosts": 100}),
    ],
)
def test_subnetting_api_operaciones_validas_responden_200(endpoint, payload):
    response = client.post(endpoint, json=payload)

    assert response.status_code == 200
    assert response.json()["subnets"]


@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        (BY_COUNT, {"network_cidr": "red-invalida", "subnet_count": 2}),
        (BY_COUNT, {"network_cidr": "192.0.2.0/30", "subnet_count": 5}),
        (BY_HOSTS, {"network_cidr": "192.0.2.0/24", "required_hosts": 1000}),
    ],
)
def test_subnetting_api_errores_de_dominio_usan_422_y_sobre_comun(endpoint, payload):
    response = client.post(endpoint, json=payload)

    assert response.status_code == 422
    assert set(response.json()) == {"error", "detail"}
    assert response.json()["error"] == "invalid_value"
    assert response.json()["detail"]


@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        (BY_COUNT, {"network_cidr": "192.0.2.0/24", "subnet_count": 0}),
        (BY_HOSTS, {"network_cidr": "192.0.2.0/24", "required_hosts": "muchos"}),
        (BY_COUNT, {"network_cidr": "192.0.2.0/24", "subnet_count": 2, "extra": True}),
    ],
)
def test_subnetting_api_errores_de_esquema_usan_422_y_sobre_comun(endpoint, payload):
    response = client.post(endpoint, json=payload)

    assert response.status_code == 422
    assert set(response.json()) == {"error", "detail"}
    assert response.json()["error"] in {"invalid_type", "invalid_value", "unknown_field"}
    assert response.json()["detail"]


@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        (BY_COUNT, {"network_cidr": "192.0.2.0/24", "subnet_count": 2}),
        (BY_HOSTS, {"network_cidr": "192.0.2.0/24", "required_hosts": 2}),
    ],
)
def test_subnetting_api_rechaza_tipo_de_contenido_no_admitido(endpoint, payload):
    response = client.post(
        endpoint,
        content=json.dumps(payload),
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 415
    assert response.json()["error"] == "unsupported_media_type"
    assert set(response.json()) == {"error", "detail"}


def test_subnetting_api_metodo_no_permitido_usa_mensaje_en_espanol():
    response = client.get(BY_COUNT)

    assert response.status_code == 405
    assert response.json()["error"] == "method_not_allowed"
    assert "método" in response.json()["detail"]
