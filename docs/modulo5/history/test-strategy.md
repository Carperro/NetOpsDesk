# Estrategia de pruebas — Historial de diagnósticos

> Cobertura prevista para la herramienta 25, pendiente de implementación. No se afirma que existan o se hayan ejecutado pruebas de History.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_history_domain.py` | Validación de campos y coordinación mediante repositorio | Pendiente de implementación |
| Repositorio | `tests/test_history_repository.py` | Inserción, default de `details`, orden descendente y borrados con SQLite `:memory:` | Pendiente de implementación |
| API | `tests/test_api_history.py` | Rutas, request/response, estados 200/201/204/422/429 y errores | Pendiente de implementación |
| Interfaz/integración | Pruebas frontend por definir | Listado, formulario manual, borrado individual y limpieza | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Crear en repositorio | Campos de entrada válidos | Fila con ID y timestamp ISO | Repositorio SQLite `:memory:` | Pendiente; no ejecutado |
| Default de detalles | Request sin `details` | Se persiste `details: ""` | Dominio/API/repositorio | Pendiente; no ejecutado |
| Campo `tool_name` ausente | Request sin `tool_name` | Rechazo de validación HTTP 422 | API | Pendiente; código de esquema según contrato común |
| Campo `action` ausente | Request sin `action` | Rechazo de validación HTTP 422 | API | Pendiente; código de esquema según contrato común |
| Listar sin entradas | Tabla vacía | HTTP 200 y colección vacía | Repositorio/API | Pendiente; no ejecutado |
| Orden del listado | Fechas distintas e IDs empatados en fecha | `created_at DESC, id DESC` | Repositorio SQLite `:memory:` | Pendiente; no ejecutado |
| Eliminar existente | ID persistido | Fila eliminada; HTTP 204 | Repositorio/API | Pendiente; no ejecutado |
| Eliminar inexistente | ID ausente | HTTP 422 `not_found` | API | Pendiente; no ejecutado |
| Limpiar historial | Varias filas en `history` y otras tablas | Elimina solo las filas de `history`; HTTP 204 | Repositorio/API | Pendiente; no ejecutado |
| Semáforo agotado | Sin permisos libres en `asyncio.Semaphore(5)` | HTTP 429 `too_many_requests` | API | Pendiente; no ejecutado |
| Registro manual | Formulario completado | Entrada aparece en el listado | Interfaz/integración | Pendiente; no ejecutado |
| Sin guardado automático | Uso de herramientas 1–24 | No se llama al repositorio de History desde esos dominios | Revisión de integración | Pendiente; integración futura fuera del alcance actual |

Las pruebas de repositorio usarán SQLite `:memory:` aislada por caso. Para comprobar el desempate, insertar registros con el mismo `created_at` y verificar que el ID mayor aparece primero.

## Ejecución y última verificación

- **Comando:** No ejecutado; esta tarea actualiza documentación.
- **Entorno:** No aplica a la tarea documental.
- **Fecha:** 2026-10-20.
- **Resultado observado:** No se ejecutaron pruebas de History.
- **Pendientes:** implementar e integrar la herramienta, confirmar obligatoriedad de `result_status` y ejecutar los casos descritos.