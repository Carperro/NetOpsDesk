# Estrategia de pruebas — Generador de comandos

> Cobertura prevista para una herramienta pendiente de implementación e integración. No se afirma que existan o se hayan ejecutado pruebas.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_command_generator_domain.py` | Whitelist, objetivos, armado, explicación y matriz `requires_admin` | Pendiente de implementación |
| API | `tests/test_api_command_generator.py` | Ruta, request/response, estados y códigos de error, semáforo | Pendiente de implementación |
| Interfaz/integración | Pruebas frontend por definir | Selector, campos dinámicos y presentación del comando como texto copiable | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Tipos permitidos | Cada uno de los cinco valores de `command_type` | Se selecciona la plantilla correspondiente | Dominio/API | Pendiente; no ejecutado |
| Tipo no permitido | `command_type` fuera de la whitelist | HTTP 422 `invalid_command_type` | API | Pendiente; no ejecutado |
| Objetivo requerido ausente | `ping`, `tracert` o `nslookup` sin objetivo | HTTP 422 `missing_target` | Dominio/API | Pendiente; no ejecutado |
| Objetivo inválido | Objetivo requerido que no sea IP ni dominio válido | HTTP 422 `invalid_target` | Dominio/API | Pendiente; sintaxis exacta por verificar |
| Objetivo opcional vacío | `ipconfig` o `netstat` con objetivo ausente o vacío | Solicitud aceptada | Dominio/API | Pendiente; no ejecutado |
| Opciones permitidas | Cada opción de cada whitelist | Se acepta y queda incorporada en el resultado | Dominio/API | Pendiente; no ejecutado |
| Opción no permitida | Opción desconocida o perteneciente a otro comando | HTTP 422 `invalid_option` | Dominio/API | Pendiente; no ejecutado |
| Privilegios de ipconfig | `/all`; luego `/flushdns`, `/release` o `/renew` | `false` para `/all`; `true` para cada una de las otras opciones | Dominio/API | Pendiente; no ejecutado |
| Privilegios de netstat | `-a` o `-n`; luego `-b` | `false` para `-a`/`-n`; `true` para `-b` | Dominio/API | Pendiente; no ejecutado |
| Otros comandos sin administrador | Opciones permitidas de `ping`, `tracert` y `nslookup` | `requires_admin: false` | Dominio/API | Pendiente; no ejecutado |
| Saturación | No hay permisos disponibles en `asyncio.Semaphore(5)` | HTTP 429 `too_many_requests` | API | Pendiente; no ejecutado |
| Solo generación | Solicitud válida | Devuelve texto; no invoca `subprocess` ni otro ejecutor | Dominio | Pendiente; no ejecutado |
| Presentación segura | Comando o explicación con caracteres especiales | Se presenta como texto, sin interpretar HTML | Interfaz | Pendiente; no ejecutado |

Los resultados de armado deben compararse con strings esperados definidos para cada plantilla. Las pruebas deben confirmar que opciones no incluidas en la whitelist no se interpolan en el comando.

## Ejecución y última verificación

- **Comando:** No ejecutado; esta tarea actualiza documentación para una herramienta pendiente.
- **Entorno:** No aplica a la tarea documental.
- **Fecha:** 2026-10-20.
- **Resultado observado:** No se ejecutaron pruebas.
- **Pendientes:** implementar e integrar dominio, API e interfaz; concretar el contrato común del Módulo 5 y ejecutar los casos descritos.