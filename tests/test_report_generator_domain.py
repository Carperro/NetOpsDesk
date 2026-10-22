"""Tests unitarios del dominio del Generador de Informes."""

import pytest
from netops_desk.exceptions import DomainError
from netops_desk.report_generator import ErrorCode, generate_report


class TestReportGeneratorSuccess:
    def test_reporte_completo(self):
        data = {
            "title": "Mi Reporte",
            "author": "Técnico",
            "date": "2023-10-27",
            "findings": [
                {"step": "Ping", "result": "OK"},
                {"step": "DNS", "result": "Falla"}
            ],
            "conclusion": "Todo mal"
        }
        md = generate_report(data=data)
        
        assert "# Mi Reporte" in md
        assert "**Técnico:** Técnico" in md
        assert "### Ping\nOK" in md
        assert "## Conclusión\nTodo mal" in md

    def test_reporte_sin_autor_ni_fecha(self):
        data = {
            "title": "Minimalista",
            "findings": [{"step": "Prueba", "result": "OK"}]
        }
        md = generate_report(data=data)
        
        assert "**Técnico:** Anónimo" in md
        assert "**Fecha:** 20" in md # Verifica que se generó la fecha de hoy (202X)


class TestReportGeneratorErrors:
    def test_titulo_vacio(self):
        with pytest.raises(DomainError) as exc:
            generate_report(data={"title": "  ", "findings": [{"step": "a", "result": "b"}]})
        assert exc.value.code == ErrorCode.MISSING_TITLE

    def test_sin_hallazgos(self):
        with pytest.raises(DomainError) as exc:
            generate_report(data={"title": "Test", "findings": []})
        assert exc.value.code == ErrorCode.EMPTY_FINDINGS

    def test_hallazgo_incompleto(self):
        with pytest.raises(DomainError) as exc:
            generate_report(data={"title": "Test", "findings": [{"step": "Ping", "result": ""}]})
        assert exc.value.code == ErrorCode.MISSING_FINDING_FIELDS

    def test_reporte_con_nulos(self):
        data = {
            "title": "Test Nulos",
            "author": None,
            "conclusion": None,
            "findings": [{"step": "Paso", "result": "OK"}]
        }
        md = generate_report(data=data)
        assert "**Técnico:** Anónimo" in md
        assert "## Conclusión" not in md        