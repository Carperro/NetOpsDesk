"""Tests de contrato HTTP del endpoint IPv6."""

import pytest
from fastapi.testclient import TestClient

from netops_desk.api.main import create_app


ENDPOINT = "/api/v1/tools/ipv6/calculate"



class TestSuccess:
    def test_slash_64(self, client: TestClient) -> None:
        response = client.post(ENDPOINT, json={"cidr": "2001:db8::/64"})
        assert response.status_code == 200
        data = response.json()
        assert data["network"] == "2001:db8::"
        assert data["last_address"] == "2001:db8::ffff:ffff:ffff:ffff"
        assert data["prefix_length"] == 64
        assert data["total_addresses"] == "18446744073709551616"
        assert data["host_bits_set"] is False
        assert data["classifications"] == []
        assert data["warnings"] == []

    def test_bits_de_host_normalizados(self, client: TestClient) -> None:
        response = client.post(ENDPOINT, json={"cidr": "2001:db8::1/64"})
        assert response.status_code == 200
        data = response.json()
        assert data["address"] == "2001:db8::1"
        assert data["network"] == "2001:db8::"
        assert data["host_bits_set"] is True
        assert len(data["warnings"]) == 1
        assert data["warnings"][0]["code"] == "host_bits_normalized"

    def test_total_addresses_es_string(self, client: TestClient) -> None:
        response = client.post(ENDPOINT, json={"cidr": "::/0"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["total_addresses"], str)
        assert data["total_addresses"] == (
            "340282366920938463463374607431768211456"
        )


class TestDomainErrors:
    def test_invalid_cidr(self, client: TestClient) -> None:
        response = client.post(ENDPOINT, json={"cidr": "not-an-ip/64"})
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "invalid_cidr"
        assert "detail" in data

    def test_invalid_prefix(self, client: TestClient) -> None:
        response = client.post(ENDPOINT, json={"cidr": "2001:db8::/129"})
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "invalid_prefix"

    def test_zone_id_not_supported(self, client: TestClient) -> None:
        response = client.post(ENDPOINT, json={"cidr": "fe80::1%eth0/64"})
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "zone_id_not_supported"


class TestPydanticErrors:
    def test_missing_cidr(self, client: TestClient) -> None:
        response = client.post(ENDPOINT, json={})
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "missing_field"

    def test_unknown_field(self, client: TestClient) -> None:
        response = client.post(
            ENDPOINT,
            json={"cidr": "2001:db8::/64", "foo": "bar"},
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "unknown_field"

    def test_wrong_type(self, client: TestClient) -> None:
        response = client.post(ENDPOINT, json={"cidr": 123})
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "invalid_type"


class TestHttpErrors:
    def test_content_type_wrong(self, client: TestClient) -> None:
        response = client.post(
            ENDPOINT,
            content="{}",
            headers={"Content-Type": "text/plain"},
        )
        assert response.status_code == 415
        data = response.json()
        assert data["error"] == "unsupported_media_type"

    def test_json_malformed(self, client: TestClient) -> None:
        response = client.post(
            ENDPOINT,
            content="{not json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "invalid_json"

    def test_method_not_allowed(self, client: TestClient) -> None:
        response = client.get(ENDPOINT)
        assert response.status_code == 405
        data = response.json()
        assert data["error"] == "method_not_allowed"
