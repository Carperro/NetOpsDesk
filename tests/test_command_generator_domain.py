"""Tests unitarios del Generador de Comandos."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.command_generator import ErrorCode, generate_command


class TestCommandGeneratorSuccess:
    def test_ping_con_opcion(self):
        res = generate_command(command_type="ping", target="8.8.8.8", options=["-t"])
        assert res["command"] == "ping -t 8.8.8.8"
        assert res["requires_admin"] is False
        assert "Ping continuo" in res["explanation"]

    def test_ipconfig_sin_target(self):
        res = generate_command(command_type="ipconfig", target=None, options=["/all"])
        assert res["command"] == "ipconfig /all"
        assert res["requires_admin"] is False

    def test_ipconfig_requiere_admin(self):
        res = generate_command(command_type="ipconfig", target=None, options=["/flushdns"])
        assert res["command"] == "ipconfig /flushdns"
        assert res["requires_admin"] is True


class TestCommandGeneratorErrors:
    def test_comando_invalido(self):
        with pytest.raises(DomainError) as exc:
            generate_command(command_type="rm -rf", target="1.1.1.1", options=[])
        assert exc.value.code == ErrorCode.INVALID_COMMAND_TYPE

    def test_falta_target(self):
        with pytest.raises(DomainError) as exc:
            generate_command(command_type="ping", target="", options=[])
        assert exc.value.code == ErrorCode.MISSING_TARGET

    def test_target_invalido(self):
        with pytest.raises(DomainError) as exc:
            generate_command(command_type="ping", target="8.8.8.8; calc.exe", options=[])
        assert exc.value.code == ErrorCode.INVALID_TARGET

    def test_opcion_invalida(self):
        with pytest.raises(DomainError) as exc:
            generate_command(command_type="ping", target="8.8.8.8", options=["-hack"])
        assert exc.value.code == ErrorCode.INVALID_OPTION