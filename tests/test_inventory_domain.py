"""Tests unitarios del dominio de inventario."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.inventory import ErrorCode, create_device, update_device, delete_device

class FakeRepo:
    def __init__(self):
        self.devices = {}
        self.next_id = 1

    def create(self, device):
        device["id"] = self.next_id
        self.devices[self.next_id] = device
        self.next_id += 1
        return device

    def get_by_id(self, device_id):
        return self.devices.get(device_id)

    def update(self, device_id, device):
        self.devices[device_id] = device
        return device

    def delete(self, device_id):
        if device_id in self.devices:
            del self.devices[device_id]
            return True
        return False

def test_crear_dispositivo_exitoso():
    repo = FakeRepo()
    res = create_device(repo=repo, data={"name": "Router", "ip_address": "192.168.1.1"})
    assert res["id"] == 1
    assert res["name"] == "Router"

def test_crear_dispositivo_ip_invalida():
    repo = FakeRepo()
    with pytest.raises(DomainError) as exc:
        create_device(repo=repo, data={"name": "Router", "ip_address": "999.999.999.999"})
    assert exc.value.code == ErrorCode.INVALID_IP

def test_crear_dispositivo_nombre_vacio():
    repo = FakeRepo()
    with pytest.raises(DomainError) as exc:
        create_device(repo=repo, data={"name": "   ", "ip_address": "192.168.1.1"})
    assert exc.value.code == ErrorCode.INVALID_NAME

def test_actualizar_inexistente():
    repo = FakeRepo()
    with pytest.raises(DomainError) as exc:
        update_device(repo=repo, device_id=99, data={"name": "X", "ip_address": "1.1.1.1"})
    assert exc.value.code == ErrorCode.NOT_FOUND