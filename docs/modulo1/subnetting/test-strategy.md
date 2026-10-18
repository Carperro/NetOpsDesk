# Estrategia de pruebas — Subnetting IPv4

## Alcance y capas

Esta estrategia describe las pruebas que existen actualmente. No convierte los comportamientos del código que siguen pendientes de definición contractual en requisitos aprobados.

| Capa | Archivo(s) | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_subnetting.py` | Cálculos por cantidad de subredes y por cantidad de hosts, normalización CIDR, capacidad y errores | Implementado |
| API | `tests/test_api_subnetting.py` | Respuestas exitosas, validación de esquema, errores de dominio, sobre JSON común, tipo de contenido y método HTTP | Implementado |
| Interfaz estática | `tests/test_frontend_static.py` | No contiene actualmente aserciones específicas de la página o el JavaScript de Subnetting | Sin cobertura específica |
| Navegador | Procedimiento manual o suite de navegador | Envío de formularios, estados de carga, resultados, advertencia de normalización y presentación visual de errores | Pendiente; no hay prueba de navegador documentada aquí |

## Matriz de casos implementados

| Caso | Entrada representativa | Resultado esperado | Prueba | Estado de ejecución |
|---|---|---|---|---|
| División por cantidad exacta | `192.168.1.0/24`, 4 subredes | Cuatro redes `/26` con límites esperados | `test_subnetting_happy_path` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Cantidad que no es potencia de dos | `192.168.1.0/24`, 3 subredes | Se devuelven tres redes del prefijo calculado `/26` | `test_subnetting_not_power_of_two` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Normalización por cantidad | `192.168.1.5/24`, 4 | Red base normalizada y `was_normalized` verdadero | `test_subnetting_normalization` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Capacidad insuficiente por cantidad | `192.168.1.0/24`, 500 | Error de dominio con capacidad máxima informada | `test_subnetting_insufficient_capacity` | Suite ejecutada: pasó en la última verificación indicada abajo |
| CIDR inválido | `esto-no-es-una-ip/24` | Error de dominio | `test_subnetting_invalid_network` | Suite ejecutada: pasó en la última verificación indicada abajo |
| División por hosts requeridos | `192.168.1.0/24`, 50 hosts | Prefijo `/26`, 62 hosts utilizables y cuatro subredes | `test_subnetting_by_hosts_happy_path` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Capacidad máxima de `/30` | `192.168.1.0/30`, 2 hosts | Una subred `/30` con dos hosts utilizables | `test_subnetting_by_hosts_max_capacity` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Capacidad insuficiente por hosts | `192.168.1.0/28`, 100 hosts | Error de dominio con máximo disponible | `test_subnetting_by_hosts_insufficient_capacity` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Normalización por hosts | `10.0.0.5/16`, 500 hosts | Red `/16` normalizada y prefijo `/23` | `test_subnetting_by_hosts_normalization` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Límites `/31` y `/32` | `/31` con 1 host; `/32` con 2 | El caso `/31` devuelve dos hosts utilizables; el `/32` solicitado falla según la implementación actual | `test_subnetting_by_hosts_slash_31_one_host`, `test_subnetting_by_hosts_slash_32_capacity` | Suite ejecutada: pasó en la última verificación indicada abajo |
| API exitosa | Solicitudes válidas a ambos endpoints | HTTP `200` y lista de subredes no vacía | `test_subnetting_api_operaciones_validas_responden_200` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Error de dominio en API | CIDR inválido o capacidad insuficiente | HTTP `422` y sobre `{error, detail}` | `test_subnetting_api_errores_de_dominio_usan_422_y_sobre_comun` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Error de esquema y campo extra | Valor cero, tipo incorrecto o campo adicional | HTTP `422` y sobre común | `test_subnetting_api_errores_de_esquema_usan_422_y_sobre_comun` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Tipo de contenido no admitido | `Content-Type: text/plain` | HTTP `415` y sobre común | `test_subnetting_api_rechaza_tipo_de_contenido_no_admitido` | Suite ejecutada: pasó en la última verificación indicada abajo |
| Método no permitido | `GET` al endpoint de cálculo | HTTP `405`, código contractual y detalle en español | `test_subnetting_api_metodo_no_permitido_usa_mensaje_en_espanol` | Suite ejecutada: pasó en la última verificación indicada abajo |

## Límites de la cobertura actual

- Las pruebas del dominio no establecen explícitamente el comportamiento requerido para entradas IPv6 en una herramienta presentada como IPv4. La aceptación de IPv6 por la ruta de Subnetting sigue siendo una cuestión contractual pendiente; estas pruebas no la resuelven.
- No hay casos específicos que impongan límites de tamaño a `subnet_count` o al número de subredes materializadas. La estrategia no interpreta la ausencia de esos casos como aceptación de colecciones ilimitadas.
- Los casos `/31` y `/32` prueban cálculos concretos, pero no cierran la discrepancia entre capacidad, rangos de hosts y serialización observada descrita en `requisitos.md` y `api-contracts.md`.
- Las pruebas HTTP usan `TestClient`; no verifican el comportamiento del navegador ni la integración visual real.
- Las pruebas estáticas generales revisan otras páginas y scripts, pero no tienen una aserción específica para los archivos HTML/JS de Subnetting.

## Ejecución y última verificación

- **Comando:** `.\.venv\Scripts\python.exe -m pytest tests/ -q`
- **Entorno:** Python 3.12, entorno virtual local del proyecto.
- **Fecha:** 2026-10-18.
- **Resultado observado:** 170 pruebas recolectadas y aprobadas, 0 fallidas, 0 omitidas (`170 passed in 1.04s`). La suite completa incluye los casos de dominio y API enumerados arriba.
- **Pendientes:** añadir pruebas específicas del frontend cuando se defina su comportamiento comprobable; resolver primero las decisiones contractuales sobre familia IP, límites de recursos y semántica `/31`/`/32`.
