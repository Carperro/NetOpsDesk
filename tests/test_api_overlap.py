from fastapi.testclient import TestClient

from netops_desk.api.main import app


client = TestClient(app)
ENDPOINT = "/api/v1/tools/overlap/calculate"


def test_api_overlap_respuesta_completa_sin_conflictos():
    response = client.post(
        ENDPOINT,
        json={"networks": ["192.0.2.0/24", "198.51.100.0/24"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"networks", "has_overlap", "overlaps"}
    assert data["has_overlap"] is False
    assert data["overlaps"] == []


def test_api_overlap_respuesta_de_conflicto_por_contencion():
    response = client.post(
        ENDPOINT,
        json={"networks": ["192.0.2.0/23", "192.0.3.0/24"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["has_overlap"] is True
    assert len(data["overlaps"]) == 1
    assert set(data["overlaps"][0]) == {"network_a", "network_b", "message"}


def test_api_overlap_normaliza_cidr_con_bits_de_host():
    response = client.post(
        ENDPOINT,
        json={"networks": ["192.0.2.10/24", "192.0.2.128/25"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["has_overlap"] is True
    assert data["networks"] == ["192.0.2.10/24", "192.0.2.128/25"]
    assert data["overlaps"][0]["network_a"] == "192.0.2.0/24"


def test_api_overlap_rechaza_menos_de_dos_redes():
    response = client.post(ENDPOINT, json={"networks": ["192.0.2.0/24"]})

    assert response.status_code == 422
    assert set(response.json()) == {"error", "detail"}


def test_api_overlap_rechaza_lista_vacia():
    response = client.post(ENDPOINT, json={"networks": []})

    assert response.status_code == 422
    assert set(response.json()) == {"error", "detail"}


def test_api_overlap_rechaza_campo_obligatorio_ausente():
    response = client.post(ENDPOINT, json={})

    assert response.status_code == 422
    assert set(response.json()) == {"error", "detail"}


def test_api_overlap_error_de_dominio_usa_contrato_comun_422():
    response = client.post(
        ENDPOINT,
        json={"networks": ["192.0.2.0/24", "red-invalida"]},
    )

    assert response.status_code == 422
    assert set(response.json()) == {"error", "detail"}
    assert response.json()["error"]
    assert response.json()["detail"]


def test_api_overlap_rechaza_tipo_de_contenido_no_admitido():
    response = client.post(
        ENDPOINT,
        content='{"networks":["192.0.2.0/24","198.51.100.0/24"]}',
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 415
    assert set(response.json()) == {"error", "detail"}


def test_api_overlap_rechaza_metodo_no_permitido_con_respuesta_json():
    response = client.get(ENDPOINT)

    assert response.status_code == 405
    assert set(response.json()) == {"error", "detail"}
