"""Tests unitarios del dominio del Asistente de Resolución."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.troubleshooter import ErrorCode, get_symptom


class TestTroubleshooterSuccess:
    def test_sintoma_sin_internet(self):
        res = get_symptom(symptom_id="sin_internet")
        assert res["symptom_name"] == "Sin acceso a internet"
        assert len(res["causes"]) >= 3
        assert len(res["causes"][0]["steps"]) >= 2

    def test_sintoma_internet_lento(self):
        res = get_symptom(symptom_id="internet_lento")
        assert res["symptom_id"] == "internet_lento"

    def test_sintoma_dns_falla(self):
        res = get_symptom(symptom_id="dns_falla")
        assert res["symptom_id"] == "dns_falla"


class TestTroubleshooterErrors:
    def test_sintoma_invalido(self):
        with pytest.raises(DomainError) as exc:
            get_symptom(symptom_id="virus_informatico")
        assert exc.value.code == ErrorCode.INVALID_SYMPTOM