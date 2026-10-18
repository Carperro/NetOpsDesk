import pytest
from fastapi.testclient import TestClient

from netops_desk.api.main import app


client = TestClient(app)


@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        ("/api/v1/tools/ipv4/calculate", {"cidr": "192.0.2.0/24", "extra": True}),
        (
            "/api/v1/tools/subnetting/by-count",
            {"network_cidr": "192.0.2.0/24", "subnet_count": 2, "extra": True},
        ),
        (
            "/api/v1/tools/subnetting/by-hosts",
            {"network_cidr": "192.0.2.0/24", "required_hosts": 2, "extra": True},
        ),
        (
            "/api/v1/tools/vlsm/calculate",
            {"network_cidr": "192.0.2.0/24", "requirements": [{"name": "LAN", "hosts": 2}], "extra": True},
        ),
        (
            "/api/v1/tools/vlsm/calculate",
            {"network_cidr": "192.0.2.0/24", "requirements": [{"name": "LAN", "hosts": 2, "extra": True}]},
        ),
        (
            "/api/v1/tools/overlap/calculate",
            {"networks": ["192.0.2.0/24", "198.51.100.0/24"], "extra": True},
        ),
    ],
)
def test_todas_las_herramientas_rechazan_campos_desconocidos(endpoint, payload):
    response = client.post(endpoint, json=payload)

    assert response.status_code == 422
    assert response.json()["error"] == "unknown_field"
    assert set(response.json()) == {"error", "detail"}
    assert "desconocido" in response.json()["detail"]
