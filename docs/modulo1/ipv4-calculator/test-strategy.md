# Estrategia y cobertura de pruebas - Calculadora IPv4/CIDR

## Alcance

Los módulos `tests/test_ipv4_domain.py`, `tests/test_api_ipv4.py`, `tests/test_frontend_static.py` y `tests/test_package_import.py` contienen las pruebas automatizadas del MVP. Cada uno cubre una capa distinta: dominio, HTTP, entrega estática y empaquetado.

Para ejecutar la suite:

```powershell
python -m pytest