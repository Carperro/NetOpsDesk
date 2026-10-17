# NetOps Desk

![Tests](https://img.shields.io/badge/tests-89%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Versión:** 0.1.0 · **Python:** 3.12+ · **Licencia:** MIT

NetOps Desk es una aplicación web local para herramientas de redes y soporte IT. El MVP implementado incluye una calculadora IPv4/CIDR, una API FastAPI y una interfaz servida por la misma aplicación. El catálogo completo del producto y las herramientas futuras se describen como alcance previsto en `docs/fundacional/`.

## Funcionalidad disponible

- Cálculo IPv4/CIDR directo mediante `cidr` o `address` + `netmask`.
- Cálculo inverso a partir de `required_hosts` y `mode`.
- Modos `conventional` y `point-to-point`, con reglas específicas para `/31` y `/32`.
- API en `POST /api/v1/tools/ipv4/calculate`.
- Interfaz web en `/`, con recursos estáticos servidos localmente.

El contrato detallado de solicitudes, respuestas y errores está en [`api-contracts.md`](docs/modulo1/ipv4-calculator/api-contracts.md). La clasificación de direcciones sigue aplazada y no forma parte de la respuesta pública actual.

## Requisitos y ejecución local

Se requiere Python 3.12 o superior. Desde la raíz del repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test,dev]"
python -m uvicorn netops_desk.api.main:app --host 127.0.0.1 --port 8000