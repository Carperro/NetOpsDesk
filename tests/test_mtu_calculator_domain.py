"""Tests unitarios del dominio de la Calculadora MTU."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.mtu_calculator import ErrorCode, calculate_mtu


class TestMtuCalculatorSuccess:
    def test_ipv4_tcp_normal(self):
        res = calculate_mtu(mtu=1500, ip_version="ipv4", transport="tcp", tunnel="none")
        assert res["mss"] == 1460
        assert res["ip_header_size"] == 20
        assert res["transport_header_size"] == 20
        assert len(res["warnings"]) == 0

    def test_ipv6_udp(self):
        res = calculate_mtu(mtu=1500, ip_version="ipv6", transport="udp", tunnel="none")
        # 1500 - 40 (IPv6) - 8 (UDP) = 1452
        assert res["mss"] == 1452

    def test_ipv4_tcp_wireguard(self):
        res = calculate_mtu(mtu=1500, ip_version="ipv4", transport="tcp", tunnel="wireguard")
        # 1500 - 20 (IPv4) - 20 (TCP) - 60 (WG) = 1400
        assert res["mss"] == 1400

    def test_mtu_bajo_advertencia(self):
        res = calculate_mtu(mtu=500, ip_version="ipv4", transport="tcp", tunnel="none")
        assert "mtu_below_minimum" in res["warnings"]

    def test_paquete_negativo(self):
        # MTU 100, IPv6 (40), TCP (20), IPSec (60). Total cabeceras = 120. Da negativo.
        res = calculate_mtu(mtu=100, ip_version="ipv6", transport="tcp", tunnel="ipsec")
        assert res["mss"] == 0
        assert "packet_too_small" in res["warnings"]


class TestMtuCalculatorErrors:
    def test_ip_invalida(self):
        with pytest.raises(DomainError) as exc:
            calculate_mtu(mtu=1500, ip_version="ipv5", transport="tcp", tunnel="none")
        assert exc.value.code == ErrorCode.INVALID_PARAMETER

    def test_transporte_invalido(self):
        with pytest.raises(DomainError) as exc:
            calculate_mtu(mtu=1500, ip_version="ipv4", transport="sctp", tunnel="none")
        assert exc.value.code == ErrorCode.INVALID_PARAMETER

    def test_tunel_invalido(self):
        with pytest.raises(DomainError) as exc:
            calculate_mtu(mtu=1500, ip_version="ipv4", transport="tcp", tunnel="vpn-inventada")
        assert exc.value.code == ErrorCode.INVALID_PARAMETER