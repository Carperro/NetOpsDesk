"""Tests unitarios del dominio IPAM."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.ipam import ErrorCode, create_ip, update_ip, delete_ip


class FakeRepo:
    def __init__(self):
        self.records = {}
        self.next_id = 1

    def create(self, record):
        if any(r["ip_address"] == record["ip_address"] for r in self.records.values()):
            raise DomainError(message="Duplicada", code="duplicate_ip")
        record["id"] = self.next_id
        self.records[self.next_id] = record
        self.next_id += 1
        return record

    def get_by_id(self, record_id):
        return self.records.get(record_id)

    def update(self, record_id, record):
        self.records[record_id] = record
        return record

    def delete(self, record_id):
        if record_id in self.records:
            del self.records[record_id]
            return True
        return False


def test_crear_ip_exitosa():
    repo = FakeRepo()
    res = create_ip(repo=repo, data={"ip_address": "192.168.1.10", "status": "assigned"})
    assert res["id"] == 1
    assert res["status"] == "assigned"

def test_crear_ip_invalida():
    repo = FakeRepo()
    with pytest.raises(DomainError) as exc:
        create_ip(repo=repo, data={"ip_address": "300.1.1.1", "status": "assigned"})
    assert exc.value.code == ErrorCode.INVALID_IP

def test_crear_estado_invalido():
    repo = FakeRepo()
    with pytest.raises(DomainError) as exc:
        create_ip(repo=repo, data={"ip_address": "192.168.1.1", "status": "hackeado"})
    assert exc.value.code == ErrorCode.INVALID_STATUS

def test_duplicado_lanzado_por_repo():
    repo = FakeRepo()
    create_ip(repo=repo, data={"ip_address": "1.1.1.1", "status": "available"})
    with pytest.raises(DomainError) as exc:
        create_ip(repo=repo, data={"ip_address": "1.1.1.1", "status": "assigned"})
    assert exc.value.code == "duplicate_ip"

def test_actualizar_inexistente():
    repo = FakeRepo()
    with pytest.raises(DomainError) as exc:
        update_ip(repo=repo, record_id=99, data={"ip_address": "1.1.1.1", "status": "available"})
    assert exc.value.code == ErrorCode.NOT_FOUND

def test_eliminar_inexistente():
    repo = FakeRepo()
    with pytest.raises(DomainError) as exc:
        delete_ip(repo=repo, record_id=99)
    assert exc.value.code == ErrorCode.NOT_FOUND