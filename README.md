# NetOps Desk

![Tests](https://img.shields.io/badge/tests-115%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Versión:** 0.1.0 · **Python:** 3.12+ · **Licencia:** MIT

NetOps Desk es una aplicación web local para herramientas de redes y soporte IT. El MVP implementado incluye la Calculadora IPv4/CIDR, Subnetting IPv4 y el Planificador VLSM, con una API FastAPI y una interfaz servida por la misma aplicación. El catálogo completo del producto y las herramientas futuras se describen en `docs/fundacional/`.

## Funcionalidad disponible

- Cálculo IPv4/CIDR directo mediante `cidr` o `address` + `netmask`.
- Cálculo inverso a partir de `required_hosts` y `mode`.
- Modos `conventional` y `point-to-point`, con reglas específicas para `/31` y `/32`.
- API en `POST /api/v1/tools/ipv4/calculate`.
- Subnetting por cantidad de subredes en `POST /api/v1/tools/subnetting/by-count`.
- Subnetting por hosts requeridos en `POST /api/v1/tools/subnetting/by-hosts`.
- Planificación VLSM en `POST /api/v1/tools/vlsm/calculate`.
- Interfaz web en `/`, con recursos estáticos servidos localmente.
- Interfaz de Subnetting IPv4 en `/tools/subnetting`.
- Planificador VLSM en `/tools/vlsm`.

El contrato detallado de solicitudes, respuestas y errores está en [`api-contracts.md`](docs/modulo1/ipv4-calculator/api-contracts.md). La clasificación de direcciones sigue aplazada y no forma parte de la respuesta pública actual.

La documentación de Subnetting está en [`docs/modulo1/subnetting/`](docs/modulo1/subnetting/) y la de VLSM en [`docs/modulo1/vlsm/`](docs/modulo1/vlsm/). La insignia refleja los 115 tests aprobados en la última ejecución de la suite; no se ejecutó la suite durante esta actualización documental.

## Requisitos y ejecución local

Se requiere Python 3.12 o superior. Desde la raíz del repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test,dev]"
python -m uvicorn netops_desk.api.main:app --host 127.0.0.1 --port 8000
