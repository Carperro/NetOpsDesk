# NetOps Desk

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
```

Abra `http://127.0.0.1:8000` en el navegador. La opción `--host 127.0.0.1` mantiene el servidor en la interfaz local.

Para ejecutar las pruebas desde el entorno virtual:

```powershell
python -m pytest
```

La lista de dependencias está en `pyproject.toml`: FastAPI, Pydantic y Uvicorn para ejecución; `httpx2` y Pytest en el grupo opcional `test`; Ruff, Black y Mypy en `dev`.

## Documentación

- `docs/fundacional/`: visión, catálogo de herramientas y principios del proyecto.
- `docs/modulo1/`: documentación del módulo de direccionamiento IP y subnetting.
- `docs/modulo1/ipv4-calculator/`: requisitos, decisiones, arquitectura, contrato de API y estrategia de pruebas de la calculadora.

La existencia de pruebas en el repositorio no implica que se hayan ejecutado en cada actualización documental; consulte el informe de verificación correspondiente para resultados de ejecución.
