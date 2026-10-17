import ipaddress

import pytest

from netops_desk.exceptions import DomainError
from netops_desk.ipv4 import calculate_direct, calculate_inverse


def codes(result):
    return [warning["code"] for warning in result["warnings"]]


@pytest.mark.parametrize(
    ("inputs", "expected", "wildcard", "normalized"),
    [
        ({"cidr": "192.168.1.0/24"}, ("192.168.1.0", "192.168.1.255", 256, 254), "0.0.0.255", False),
        ({"address": "10.0.0.1", "netmask": "255.0.0.0"}, ("10.0.0.0", "10.255.255.255", 16_777_216, 16_777_214), "0.255.255.255", True),
        ({"cidr": "172.16.1.5/12"}, ("172.16.0.0", "172.31.255.255", 1_048_576, 1_048_574), "0.15.255.255", True),
        ({"cidr": "0.0.0.1/0"}, ("0.0.0.0", "255.255.255.255", 4_294_967_296, 4_294_967_294), "255.255.255.255", True),
    ],
)
def test_direct_regular_networks_and_normalization(inputs, expected, wildcard, normalized):
    result = calculate_direct(**inputs)
    assert (result["network"], result["broadcast"], result["total_addresses"], result["usable_addresses"]) == expected
    assert result["wildcard"] == wildcard
    assert ("host_bits_normalized" in codes(result)) is normalized


@pytest.mark.parametrize(
    ("cidr", "mode", "total", "usable", "broadcast", "first", "last"),
    [
        ("192.0.2.1/31", "conventional", 2, 0, None, None, None),
        ("192.0.2.1/32", "conventional", 1, 0, None, None, None),
        ("192.0.2.1/31", "point-to-point", 2, 2, None, "192.0.2.0", "192.0.2.1"),
        ("192.0.2.1/32", "point-to-point", 1, 1, None, "192.0.2.1", "192.0.2.1"),
    ],
)
def test_direct_31_and_32(cidr, mode, total, usable, broadcast, first, last):
    result = calculate_direct(cidr=cidr, mode=mode)
    assert result["total_addresses"] == total
    assert result["usable_addresses"] == usable
    assert result["broadcast"] is broadcast
    assert result["first_usable"] == first
    assert result["last_usable"] == last


def test_direct_point_to_point_fallback_and_warning():
    result = calculate_direct(cidr="192.0.2.1/30", mode="point-to-point")
    assert result["network"] == "192.0.2.0"
    assert result["broadcast"] == "192.0.2.3"
    assert result["first_usable"] == "192.0.2.1"
    assert result["last_usable"] == "192.0.2.2"
    assert result["usable_addresses"] == 2
    assert codes(result) == ["host_bits_normalized", "point_to_point_not_applicable"]


def test_direct_30_conventional():
    result = calculate_direct(cidr="192.0.2.1/30", mode="conventional")
    assert result["total_addresses"] == 4
    assert result["usable_addresses"] == 2
    assert result["broadcast"] == "192.0.2.3"
    assert result["first_usable"] == "192.0.2.1"
    assert result["last_usable"] == "192.0.2.2"
    assert codes(result) == ["host_bits_normalized"]


def test_direct_binary_matches_fields_and_has_exact_keys():
    result = calculate_direct(cidr="192.0.2.1/31", mode="conventional")
    binary = result["binary"]
    assert set(binary) == {"network", "broadcast", "netmask", "wildcard", "first_usable", "last_usable"}
    for field, value in binary.items():
        original = result[field]
        if original is None:
            assert value is None
        else:
            assert value == ".".join(f"{int(octet):08b}" for octet in original.split("."))
            assert all(len(octet) == 8 for octet in value.split("."))


@pytest.mark.parametrize(
    ("hosts", "mode", "prefix", "total", "usable", "applied", "warning"),
    [
        (1, "conventional", 30, 4, 2, "conventional", None),
        (1, "point-to-point", 32, 1, 1, "point-to-point", None),
        (2, "point-to-point", 31, 2, 2, "point-to-point", None),
        (3, "point-to-point", 29, 8, 6, "conventional", "point_to_point_not_applicable"),
        (4_294_967_294, "conventional", 0, 4_294_967_296, 4_294_967_294, "conventional", None),
    ],
)
def test_inverse_selection(hosts, mode, prefix, total, usable, applied, warning):
    result = calculate_inverse(required_hosts=hosts, mode=mode)
    assert result["prefix"] == prefix
    assert result["total_addresses"] == total
    assert result["usable_addresses"] == usable
    assert result["mode_requested"] == mode
    assert result["mode_applied"] == applied
    assert codes(result) == ([] if warning is None else [warning])
    assert set(result) == {"required_hosts", "mode_requested", "mode_applied", "prefix", "total_addresses", "usable_addresses", "warnings"}


@pytest.mark.parametrize(
    ("call", "code"),
    [
        (lambda: calculate_direct(cidr="192.0.2.1/33"), "invalid_value"),
        (lambda: calculate_direct(cidr="999.0.0.1/24"), "invalid_value"),
        (lambda: calculate_direct(address="192.0.2.1", netmask="255.0.255.0"), "non_contiguous_netmask"),
        (lambda: calculate_direct(address="192.0.2.1"), "missing_field"),
        (lambda: calculate_direct(cidr="192.0.2.1/24", address="192.0.2.1", netmask="255.255.255.0"), "incompatible_inputs"),
        (lambda: calculate_inverse(required_hosts=4_294_967_295, mode="conventional"), "insufficient_capacity"),
        (lambda: calculate_inverse(required_hosts=0, mode="conventional"), "invalid_value"),
        (lambda: calculate_inverse(required_hosts=True, mode="conventional"), "invalid_type"),
        (lambda: calculate_inverse(required_hosts=1, mode="other"), "invalid_value"),
    ],
)
def test_invalid_domain_inputs_have_stable_codes(call, code):
    with pytest.raises(DomainError) as caught:
        call()
    assert caught.value.code == code


def test_inverse_prefix_is_longest_that_satisfies_capacity():
    for hosts, mode in ((1, "conventional"), (1, "point-to-point"), (2, "point-to-point"), (3, "point-to-point")):
        result = calculate_inverse(required_hosts=hosts, mode=mode)
        assert result["usable_addresses"] >= hosts
        if result["prefix"] < 32:
            larger_prefix = result["prefix"] + 1
            total = 1 << (32 - larger_prefix)
            if mode == "point-to-point" and larger_prefix in (31, 32):
                capacity = total
            else:
                capacity = max(0, total - 2) if larger_prefix < 31 else 0
            assert capacity < hosts


def test_all_direct_network_fields_are_ipv4_values_when_not_null():
    result = calculate_direct(cidr="203.0.113.7/27")
    for key in ("network", "broadcast", "netmask", "wildcard", "first_usable", "last_usable"):
        if result[key] is not None:
            assert isinstance(ipaddress.IPv4Address(result[key]), ipaddress.IPv4Address)
