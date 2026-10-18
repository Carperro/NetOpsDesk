# NetOps Desk

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Versión:** 0.1.0 · **Python:** 3.12+ · **Licencia:** MIT

NetOps Desk es una aplicación web local para herramientas de redes y soporte IT. El MVP comprende las 25 herramientas del catálogo. Su desarrollo e integración con el frontend avanzan progresivamente. Actualmente hay cuatro herramientas desplegadas: la Calculadora IPv4/CIDR, Subnetting IPv4, el Planificador VLSM y el Detector de solapamiento. La API FastAPI y la interfaz se sirven desde la misma aplicación.

## Funcionalidad disponible

- Cálculo IPv4/CIDR directo mediante `cidr` o `address` + `netmask`.
- Cálculo inverso a partir de `required_hosts` y `mode`.
- Modos `conventional` y `point-to-point`, con reglas específicas para `/31` y `/32`.
- API en `POST /api/v1/tools/ipv4/calculate`.
- Subnetting por cantidad de subredes en `POST /api/v1/tools/subnetting/by-count`.
- Subnetting por hosts requeridos en `POST /api/v1/tools/subnetting/by-hosts`.
- Planificación VLSM en `POST /api/v1/tools/vlsm/calculate`.
- Detección de solapamientos en `POST /api/v1/tools/overlap/calculate`.
- Interfaz web en `/`, con recursos estáticos servidos localmente.
- Interfaz de Subnetting IPv4 en `/tools/subnetting`.
- Planificador VLSM en `/tools/vlsm`.
- Detector de solapamiento en `/tools/overlap`.

El contrato detallado de solicitudes, respuestas y errores está en [`api-contracts.md`](docs/modulo1/ipv4-calculator/api-contracts.md). La clasificación de direcciones sigue aplazada y no forma parte de la respuesta pública actual.

La documentación de API común del Módulo 1 está en [`docs/modulo1/api-contracts.md`](docs/modulo1/api-contracts.md). La documentación de Subnetting está en [`docs/modulo1/subnetting/`](docs/modulo1/subnetting/), la de VLSM en [`docs/modulo1/vlsm/`](docs/modulo1/vlsm/) y la del Detector de solapamiento en [`docs/modulo1/overlap/`](docs/modulo1/overlap/).

## Requisitos y ejecución local

Se requiere Python 3.12 o superior. Desde la raíz del repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install pip-tools
pip-sync requirements.lock
python -m pip install --no-deps -e .
pre-commit install
python -m uvicorn netops_desk.api.main:app --host 127.0.0.1 --port 8000
```

El lockfile fija las dependencias de pruebas y desarrollo. Para regenerarlo después de modificar `pyproject.toml`, ejecutá `pip-compile --extra test --extra dev --generate-hashes --allow-unsafe --strip-extras --output-file requirements.lock pyproject.toml` y revisá el diff antes de compartirlo.

`pre-commit install` activa el hook local. Antes de cada commit ejecuta Ruff para errores críticos y la suite completa de Pytest. El conjunto completo de reglas Ruff todavía requiere una limpieza independiente del código existente.
