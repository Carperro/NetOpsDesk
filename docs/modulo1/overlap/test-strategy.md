# Estrategia de pruebas — Detector de solapamiento

## Cobertura implementada

| Capa | Archivo | Cobertura observada |
|---|---|---|
| Dominio | `tests/test_overlap.py` | Redes independientes, solapamiento parcial, contención, mínimo de entradas, CIDR inválido, IPv6 rechazado, redes adyacentes, redes iguales/contenidas, normalización y conservación de entrada, todos los pares y orden de salida. |
| API | `tests/test_api_overlap.py` | Respuesta completa con/sin conflicto, contención, normalización, entrada insuficiente/vacía/ausente, error de dominio, Content-Type 415 y método 405. |
| Interfaz estática | `tests/test_frontend_static.py` | Ruta HTML, script y contenedores, uso de texto seguro para errores/datos dinámicos y carga del formateador común. |

## Cobertura que no se debe dar por ejecutada

- Las pruebas estáticas del frontend no simulan interacción real en un navegador.
- `test_api_overlap.py` no prueba específicamente JSON malformado 400 ni excepción inesperada 500; ambos se rigen por handlers comunes y tienen cobertura en pruebas compartidas/de IPv4.
- No se encuentra prueba de límite superior de cantidad de redes, porque el contrato todavía no define ese límite.
- Las fuentes independientes de los valores esperados de red no están registradas en esta estrategia.

## Última verificación observada

- **Comando:** `\.venv\Scripts\python.exe -m pytest tests/ -q`
- **Fecha:** 2026-10-18
- **Resultado:** 170 pruebas aprobadas en la suite completa (verificación ejecutada antes de esta actualización documental).
- **Alcance:** este registro no afirma que una prueba de navegador ni un benchmark se hayan ejecutado.
