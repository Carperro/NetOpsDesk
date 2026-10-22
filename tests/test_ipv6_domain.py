"""Tests unitarios del dominio IPv6/CIDR."""

import pytest

from netops_desk.exceptions import DomainError
from netops_desk.ipv6 import ErrorCode, calculate


class TestValidInputs:
    def test_slash_64_sin_bits_de_host(self):
        result = calculate(cidr="2001:db8::/64")
        assert result["network"] == "2001:db8::"
        assert result["last_address"] == "2001:db8::ffff:ffff:ffff:ffff"
        assert result["prefix_length"] == 64
        assert result["address"] == "2001:db8::"
        assert result["host_bits_set"] is False
        assert result["warnings"] == []
        assert result["classifications"] == []
        assert result["total_addresses"] == "18446744073709551616"

    def test_slash_128(self):
        result = calculate(cidr="::1/128")
        assert result["network"] == "::1"
        assert result["last_address"] == "::1"
        assert result["total_addresses"] == "1"

    def test_slash_0(self):
        result = calculate(cidr="::/0")
        assert result["network"] == "::"
        assert result["last_address"] == (
            "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
        )
        assert result["total_addresses"] == (
            "340282366920938463463374607431768211456"
        )

    def test_bits_de_host_normalizados(self):
        result = calculate(cidr="2001:db8::1/64")
        assert result["address"] == "2001:db8::1"
        assert result["network"] == "2001:db8::"
        assert result["host_bits_set"] is True
        assert len(result["warnings"]) == 1
        assert result["warnings"][0]["code"] == "host_bits_normalized"

    def test_canonicalizacion_rfc_5952(self):
        result = calculate(cidr="2001:0DB8:0000:0000:0000:0000:0000:0001/64")
        assert result["address"] == "2001:db8::1"
        assert result["network"] == "2001:db8::"

    def test_total_addresses_es_string(self):
        result = calculate(cidr="2001:db8::/64")
        assert isinstance(result["total_addresses"], str)

    def test_input_preserva_cadena_original(self):
        original = "2001:0DB8::/64"
        result = calculate(cidr=original)
        assert result["input"] == original

    def test_ipv4_mapped_aceptada(self):
        result = calculate(cidr="::ffff:192.0.2.1/128")
        assert result["network"] == "::ffff:c000:201"
        assert result["host_bits_set"] is False


class TestInvalidInputs:
    def test_cidr_no_string(self):
        with pytest.raises(DomainError) as exc_info:
            calculate(cidr=123)
        assert exc_info.value.code == ErrorCode.INVALID_CIDR

    def test_cidr_sin_barra(self):
        with pytest.raises(DomainError) as exc_info:
            calculate(cidr="2001:db8::")
        assert exc_info.value.code == ErrorCode.INVALID_CIDR

    def test_cidr_con_dos_barras(self):
        with pytest.raises(DomainError) as exc_info:
            calculate(cidr="2001:db8::/64/128")
        assert exc_info.value.code == ErrorCode.INVALID_CIDR

    def test_ipv6_invalida(self):
        with pytest.raises(DomainError) as exc_info:
            calculate(cidr="not-an-ip/64")
        assert exc_info.value.code == ErrorCode.INVALID_CIDR

    def test_ipv4_como_string(self):
        with pytest.raises(DomainError) as exc_info:
            calculate(cidr="192.168.1.1/24")
        assert exc_info.value.code == ErrorCode.INVALID_CIDR

    def test_prefix_no_entero(self):
        with pytest.raises(DomainError) as exc_info:
            calculate(cidr="2001:db8::/abc")
        assert exc_info.value.code == ErrorCode.INVALID_PREFIX

    def test_prefix_negativo(self):
        with pytest.raises(DomainError) as exc_info:
            calculate(cidr="2001:db8::/-1")
        assert exc_info.value.code == ErrorCode.INVALID_PREFIX

    def test_prefix_vacio(self):
        with pytest.raises(DomainError) as exc_info:
            calculate(cidr="2001:db8::/")
        assert exc_info.value.code == ErrorCode.INVALID_PREFIX

    def test_prefix_mayor_128(self):
        with pytest.raises(DomainError) as exc_info:
            calculate(cidr="2001:db8::/129")
        assert exc_info.value.code == ErrorCode.INVALID_PREFIX

    def test_zone_id_rechazado(self):
        with pytest.raises(DomainError) as exc_info:
            calculate(cidr="fe80::1%eth0/64")
        assert exc_info.value.code == ErrorCode.ZONE_ID_NOT_SUPPORTED