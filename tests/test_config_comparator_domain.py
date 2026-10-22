"""Tests unitarios del dominio del Comparador de Configuraciones."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.config_comparator import ErrorCode, compare_configs


class TestConfigComparatorSuccess:
    def test_configuraciones_identicas(self):
        config = "hostname Router1\ninterface Gi0/1"
        res = compare_configs(config_a=config, config_b=config)
        
        assert res["has_changes"] is False
        assert res["diff_lines"] == []

    def test_configuraciones_diferentes(self):
        config_a = "hostname Router1\ninterface Gi0/1\n ip address 192.168.1.1 255.255.255.0"
        config_b = "hostname Router1\ninterface Gi0/1\n ip address 192.168.1.2 255.255.255.0"
        
        res = compare_configs(config_a=config_a, config_b=config_b)
        
        assert res["has_changes"] is True
        assert len(res["diff_lines"]) > 0
        
        # Validar que difflib generó las líneas correctas
        diff_text = "\n".join(res["diff_lines"])
        assert "--- Config A" in diff_text
        assert "+++ Config B" in diff_text
        assert "- ip address 192.168.1.1 255.255.255.0" in diff_text
        assert "+ ip address 192.168.1.2 255.255.255.0" in diff_text

    def test_un_lado_vacio(self):
        res = compare_configs(config_a="hostname Router", config_b="")
        assert res["has_changes"] is True
        assert len(res["diff_lines"]) > 0


class TestConfigComparatorErrors:
    def test_ambos_vacios(self):
        with pytest.raises(DomainError) as exc:
            compare_configs(config_a="   ", config_b="")
        
        assert exc.value.code == ErrorCode.EMPTY_CONFIGS