# Estrategia y cobertura de pruebas - Calculadora IPv4/CIDR

## Alcance

Los módulos `tests/test_ipv4_domain.py`, `tests/test_api_ipv4.py`, `tests/test_subnetting.py`, `tests/test_frontend_static.py` y `tests/test_package_import.py` contienen las pruebas automatizadas del MVP. `test_subnetting.py` cubre el dominio de Subnetting; no hay actualmente una suite HTTP dedicada a sus endpoints. La cobertura estática de `test_frontend_static.py` se centra en IPv4 y recursos compartidos, por lo que la nueva herramienta aún requiere cobertura específica de API y frontend.

Para ejecutar la suite:

```powershell
python -m pytest
