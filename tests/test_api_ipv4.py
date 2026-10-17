"""
Integración de pruebas para la API IPv4/CIDR usando TestClient.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from netops_desk.api.main import app

client = TestClient(app)


def test_direct_cidr_valid():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == "192.168.1.0"
    assert data["broadcast"] == "192.168.1.255"
    assert data["netmask"] == "255.255.255.0"
    assert data["wildcard"] == "0.0.0.255"
    assert data["first_usable"] == "192.168.1.1"
    assert data["last_usable"] == "192.168.1.254"
    assert data["total_addresses"] == 256
    assert data["usable_addresses"] == 254
    assert data["binary"]["network"] == "11000000.10101000.00000001.00000000"
    assert data["binary"]["broadcast"] == "11000000.10101000.00000001.11111111"
    assert data["binary"]["netmask"] == "11111111.11111111.11111111.00000000"
    assert data["binary"]["wildcard"] == "00000000.00000000.00000000.11111111"
    assert data["binary"]["first_usable"] == "11000000.10101000.00000001.00000001"
    assert data["binary"]["last_usable"] == "11000000.10101000.00000001.11111110"
    assert data["warnings"] == []


def test_direct_address_netmask_valid():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"address": "10.0.0.1", "netmask": "255.0.0.0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == "10.0.0.0"
    assert data["broadcast"] == "10.255.255.255"
    assert data["netmask"] == "255.0.0.0"
    assert data["wildcard"] == "0.255.255.255"
    assert data["first_usable"] == "10.0.0.1"
    assert data["last_usable"] == "10.255.255.254"
    assert data["total_addresses"] == 16777216
    assert data["usable_addresses"] == 16777214
    assert data["warnings"] == [{
        "code": "host_bits_normalized",
        "message": "La dirección contenía bits de host; se calculó la dirección de red."
    }]


def test_direct_host_bits_normalized():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.5/24"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == "192.168.1.0"
    assert data["broadcast"] == "192.168.1.255"
    assert data["warnings"] == [{
        "code": "host_bits_normalized",
        "message": "La dirección contenía bits de host; se calculó la dirección de red."
    }]


def test_direct_point_to_point_31():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.0.2.1/31", "mode": "point-to-point"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == "192.0.2.0"
    assert data["broadcast"] is None
    assert data["netmask"] == "255.255.255.254"
    assert data["wildcard"] == "0.0.0.1"
    assert data["first_usable"] == "192.0.2.0"
    assert data["last_usable"] == "192.0.2.1"
    assert data["total_addresses"] == 2
    assert data["usable_addresses"] == 2
    assert data["warnings"] == [{
        "code": "host_bits_normalized",
        "message": "La dirección contenía bits de host; se calculó la dirección de red."
    }]


def test_direct_point_to_point_32():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.0.2.1/32", "mode": "point-to-point"},
    )
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == "192.0.2.1"
    assert data["broadcast"] is None
    assert data["netmask"] == "255.255.255.255"
    assert data["wildcard"] == "0.0.0.0"
    assert data["first_usable"] == "192.0.2.1"
    assert data["last_usable"] == "192.0.2.1"
    assert data["total_addresses"] == 1
    assert data["usable_addresses"] == 1
    assert data["warnings"] == []


def test_direct_point_to_point_fallback():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.0.2.1/30", "mode": "point-to-point"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == "192.0.2.0"
    assert data["broadcast"] == "192.0.2.3"
    assert data["first_usable"] == "192.0.2.1"
    assert data["last_usable"] == "192.0.2.2"
    assert data["total_addresses"] == 4
    assert data["usable_addresses"] == 2
    assert data["warnings"] == [
        {
            "code": "host_bits_normalized",
            "message": "La dirección contenía bits de host; se calculó la dirección de red."
        },
        {
            "code": "point_to_point_not_applicable",
            "message": "Point-to-point no aplica al prefijo seleccionado; se aplicó conventional."
        }
    ]


def test_inverse_valid():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"required_hosts": 1, "mode": "point-to-point"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["required_hosts"] == 1
    assert data["mode_requested"] == "point-to-point"
    assert data["mode_applied"] == "point-to-point"
    assert data["prefix"] == 32
    assert data["total_addresses"] == 1
    assert data["usable_addresses"] == 1
    assert data["warnings"] == []


def test_inverse_point_to_point_fallback():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"required_hosts": 3, "mode": "point-to-point"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["required_hosts"] == 3
    assert data["mode_requested"] == "point-to-point"
    assert data["mode_applied"] == "conventional"
    assert data["prefix"] == 29
    assert data["total_addresses"] == 8
    assert data["usable_addresses"] == 6
    assert data["warnings"] == [{
        "code": "point_to_point_not_applicable",
        "message": "Point-to-point no aplica al prefijo seleccionado; se aplicó conventional."
    }]


def test_unknown_field():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24", "foo": "bar"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "unknown_field"
    assert "foo" in data["detail"]


def test_missing_field_direct():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"address": "192.168.1.1"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "missing_field"
    assert "juntos" in data["detail"].lower()


def test_incompatible_inputs():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24", "address": "10.0.0.1", "netmask": "255.255.255.0"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "incompatible_inputs"
    assert "excluyentes" in data["detail"].lower()

def test_direct_inverse_mixing():
    payloads = [
        {"cidr": "192.168.1.0/24", "required_hosts": 3},
        {"cidr": "192.168.1.0/24", "required_hosts": 3, "mode": "conventional"},
    ]
    for payload in payloads:
        response = client.post("/api/v1/tools/ipv4/calculate", json=payload)
        assert response.status_code == 422
        assert response.json()["error"] == "incompatible_inputs"

def test_invalid_type_cidr():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": 123},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_type"
    assert "cidr" in data["detail"]
    assert "cadena" in data["detail"]

def test_invalid_value_prefix():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/33"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_value"
    assert "cidr" in data["detail"]
    assert "prefijo" in data["detail"]


def test_invalid_ipv4_address():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"address": "999.0.0.1", "netmask": "255.255.255.0"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_value"
    assert set(data) == {"error", "detail"}
    assert isinstance(data["detail"], str)


def test_invalid_ipv4_netmask():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"address": "192.0.2.1", "netmask": "255.999.255.0"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_value"
    assert set(data) == {"error", "detail"}
    assert isinstance(data["detail"], str)


def test_non_contiguous_netmask():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"address": "192.168.1.1", "netmask": "255.0.255.0"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "non_contiguous_netmask"
    assert "máscara" in data["detail"].lower()
    assert "contigua" in data["detail"].lower()

def test_json_malformed():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        content=b"{not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_json"


def test_json_invalid_utf8_bytes():
    # Bytes que no son UTF-8 válido: FastAPI devuelve 400 antes de validar.
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        content=b"\xff",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "invalid_json"
    assert "cuerpo" in data["detail"].lower()

def test_content_type_wrong():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        content=b"cidr=192.168.1.0/24",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 415
    data = response.json()
    assert data["error"] == "unsupported_media_type"


def test_method_not_allowed():
    response = client.get("/api/v1/tools/ipv4/calculate")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    assert response.status_code == 405
    data = response.json()
    assert data["error"] == "method_not_allowed"


def test_insufficient_capacity():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"required_hosts": 4294967295, "mode": "conventional"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "insufficient_capacity"


def test_required_hosts_zero():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"required_hosts": 0, "mode": "conventional"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_value"


def test_required_hosts_bool():
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"required_hosts": True, "mode": "conventional"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_type"

def test_unexpected_exception_returns_500(monkeypatch):
    """Un error inesperado en el dominio devuelve 500 uniforme."""
    def mock_calculate(*args, **kwargs):
        raise ValueError("unexpected")
    monkeypatch.setattr("netops_desk.api.routes.ipv4.calculate_direct", mock_calculate)
    from fastapi.testclient import TestClient
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post("/api/v1/tools/ipv4/calculate", json={"cidr":"192.168.1.0/24"})
    assert response.status_code == 500
    assert response.json() == {
        "error": "internal_error",
        "detail": "Error interno del servidor.",
    }


def test_unexpected_exception_during_body_read(monkeypatch):
    """Si falla la lectura del cuerpo, FastAPI responde 400 uniforme.

    Nota: con el refactor, la lectura del cuerpo la hace FastAPI, no el
    endpoint. Un fallo interno de lectura se convierte en 400 con un
    mensaje contractual ('invalid_json'). El comportamiento anterior
    (500) aplicaba cuando el endpoint leía el body manualmente.
    """
    from starlette.requests import Request

    original_body = Request.body

    async def mock_body(self):
        if (
            self.url.path == "/api/v1/tools/ipv4/calculate"
            and self.headers.get("x-test-body-read-failure") == "1"
        ):
            raise RuntimeError("unexpected body read failure")
        return await original_body(self)

    monkeypatch.setattr(Request, "body", mock_body)
    from fastapi.testclient import TestClient
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24"},
        headers={"x-test-body-read-failure": "1"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": "invalid_json",
        "detail": "El cuerpo de la petición no es JSON válido.",
    }

def test_content_type_precedes_json_validation():
    # Wrong Content-Type should be caught before JSON validation
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        content=b"not json",
        headers={"Content-Type": "text/plain"},
    )
    assert response.status_code == 415
    data = response.json()
    assert data["error"] == "unsupported_media_type"


def test_unknown_field_precedes_incompatibility():
    # Unknown field should be caught before incompatibility check
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24", "required_hosts": 3, "mode": "conventional", "foo": "bar"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "unknown_field"
    assert "foo" in data["detail"]

def test_content_type_missing():
    # La ausencia de Content-Type se valida antes que el cuerpo.
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        content='{"cidr": "192.168.1.0/24"}',
        headers={},
    )
    assert response.request.headers.get("content-type") is None
    assert response.status_code == 415
    data = response.json()
    assert data["error"] == "unsupported_media_type"


def test_invalid_body_not_object():
    # El JSON es válido, pero el valor superior no es un objeto.
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json=["not", "an", "object"],
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_body"


def test_multiple_unknown_fields():
    # Los campos desconocidos se informan en orden alfabético estable.
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24", "foo": 1, "bar": 2},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "unknown_field"
    assert "bar" in data["detail"]
    assert "foo" in data["detail"]
    assert data["detail"].index("bar") < data["detail"].index("foo")


def test_missing_field_inverse():
    # El cálculo inverso requiere required_hosts y mode.
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"required_hosts": 3},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "missing_field"
    assert "mode" in data["detail"]


def test_method_precedes_body():
    # El método debe validarse antes que la sintaxis del cuerpo.
    response = client.request(
        "GET",
        "/api/v1/tools/ipv4/calculate",
        content='{not json',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 405
    data = response.json()
    assert data["error"] == "method_not_allowed"


def test_incompatible_precedes_missing():
    # La incompatibilidad se informa antes que la falta de netmask.
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24", "address": "192.0.2.1"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "incompatible_inputs"


def test_incompatible_precedes_invalid_type():
    # La incompatibilidad se informa antes de validar el tipo de address.
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"cidr": "192.168.1.0/24", "address": 123},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "incompatible_inputs"


def test_missing_precedes_invalid_type():
    # La falta de netmask se informa antes de validar address.
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"address": 123},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "missing_field"


def test_invalid_value_precedes_netmask():
    # El valor IPv4 inválido se valida antes que la contigüidad de la máscara.
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"address": "not-an-ipv4", "netmask": "255.0.255.0"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_value"


def test_invalid_type_precedes_netmask():
    # El tipo incorrecto (address como int) se valida antes que la contigüidad de la máscara.
    response = client.post(
        "/api/v1/tools/ipv4/calculate",
        json={"address": 123, "netmask": "255.0.255.0"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_type"


if __name__ == "__main__":
    # For manual execution; normally run via pytest.
    pass