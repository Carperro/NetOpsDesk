# Estrategia de pruebas — Gestor de direcciones IP (IPAM)

> Cobertura parcial observada en el árbol de trabajo. Las pruebas de dominio, repositorio y API existen sin seguimiento por Git. No se ejecutaron pruebas durante esta actualización documental; la cobertura de semáforo/429 aún falta.

## Alcance y capas

| Capa | Archivo(s) previstos | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_ipam_domain.py` | Crear válido, IPv4 y estado inválidos, duplicado por repo FakeRepo, update/delete inexistentes | Parcial; archivo sin seguimiento |
| Repositorio | `tests/test_ipam_repository.py` | Crear/listar con SQLite `:memory:` y traducir IP duplicada a `DomainError(duplicate_ip)` | Parcial; archivo sin seguimiento |
| API | `tests/test_api_ipam.py` | CRUD, duplicado e IP inválida con TestClient y repositorio `:memory:` | Parcial; archivo sin seguimiento, falta caso de saturación 429 |
| Frontend/integración | `src/netops_desk/static/tools/ipam.html`, `static/js/ipam.js`, `static/css/ipam.css` | Recursos presentes; falta prueba de integración visual/estática | Sin cobertura identificada |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba prevista | Estado de ejecución |
|---|---|---|---|---|
| Crear dominio | IPv4 válida y `assigned` | Registro con ID asignado y estado esperado | `test_crear_ip_exitosa` | Implementado; no ejecutado en esta tarea |
| Rechazar IPv4 inválida | `300.1.1.1` | `DomainError(invalid_ip)` | `test_crear_ip_invalida` | Implementado; no ejecutado en esta tarea |
| Rechazar estado inválido | `status="hackeado"` | `DomainError(invalid_status)` | `test_crear_estado_invalido` | Implementado; no ejecutado en esta tarea |
| Duplicado en FakeRepo | Crear dos registros con misma IP | `DomainError(duplicate_ip)` | `test_duplicado_lanzado_por_repo` | Implementado; no ejecutado en esta tarea |
| Actualizar/eliminar ID inexistente | ID 99 | `DomainError(not_found)` | `test_actualizar_inexistente`, `test_eliminar_inexistente` | Implementado; no ejecutado en esta tarea |
| Crear/listar en SQLite | Registro IPv4 y `assigned` | ID asignado y registro recuperable | `test_crear_y_listar` | Implementado; no ejecutado en esta tarea |
| Listar vacío y con registros | Repositorio vacío/precargado | Lista vacía o registros almacenados | Repositorio en memoria y API GET | Pendiente |
| Actualizar y eliminar | ID existente | Cambios persistidos; DELETE sin cuerpo | CRUD del repositorio y API PUT/DELETE | Pendiente |
| Reemplazo completo PUT | Omitir `assigned_to` o `notes` del request | El campo omitido queda en `""`; el resto del registro refleja el request | Test API de PUT y lectura posterior | Pendiente |
| IPv4 inválida | `999.999.999.999` | `DomainError(invalid_ip)`; API 422 | Dominio con FakeRepo y contrato API | Pendiente |
| Estado inválido | `status="unknown"` | `DomainError(invalid_status)`; API 422 | Dominio con FakeRepo y contrato API | Pendiente |
| Dirección duplicada al crear | Misma IP dos veces | La restricción UNIQUE impide segunda fila; repositorio produce `duplicate_ip`; API responde 422 | `test_error_ip_duplicada`, `test_crud_ipam_completo` | Presente sin seguimiento; no ejecutado aquí |
| Contrato CRUD HTTP | Crear duplicado, listar, actualizar estado y eliminar | 201, 422, 200, 204 y lista vacía posterior | `test_crud_ipam_completo` | Presente sin seguimiento; no ejecutado aquí |
| IP inválida por API | Request con IP inválida | HTTP 422 `invalid_ip` | `test_crear_ip_invalida_api` | Presente sin seguimiento; no ejecutado aquí |
| Dirección duplicada al editar | Cambiar una fila a IP de otra | Sin colisión persistida; error `duplicate_ip` | SQLite `:memory:` y API PUT 422 | Pendiente |
| ID inexistente | PUT/DELETE con ID ausente | `not_found`; API 422 | Dominio y contrato API | Pendiente |
| Semáforo agotado | Cinco operaciones ocupan los permisos y llega otra solicitud | HTTP 429 con `too_many_requests`, sin espera | Test de contrato API con semáforo controlado | Pendiente |
| Campos del request | Faltantes, extra o tipo incorrecto | Error de validación 422 según contrato | API TestClient | Pendiente |
| Aislamiento de pruebas | Dependencia API sustituida | No lee ni modifica `netops.db` de desarrollo | Fixture de TestClient con `SQLiteIPAMRepository(":memory:")` | Pendiente |

Las pruebas de dominio deben usar un FakeRepo para no depender de SQLite. Las pruebas del repositorio usan SQLite en memoria y comprueban que la operación pública del repositorio traduce la violación de unicidad a `DomainError(duplicate_ip)`; la prueba no debe esperar que ese error interno de SQLite escape sin traducir.

Los resultados esperados para IPv4 deben basarse en la validación de la biblioteca estándar `ipaddress`; los estados válidos provienen de DEC-IPAM-02 y la unicidad de la restricción SQLite definida por DEC-IPAM-01.

## Ejecución y última verificación

- **Comando:** no ejecutado; esta tarea solo crea documentación.
- **Entorno:** Python 3.12, FastAPI, Pydantic y Pytest según la documentación del proyecto; existen pruebas IPAM en la copia de trabajo, pero no se ejecutaron durante esta tarea.
- **Fecha:** 2026-10-20.
- **Resultado observado:** no ejecutado durante esta tarea; las pruebas listadas existen estáticamente, sin verificación de que pasen.
- **Pendientes:** completar pruebas de update/delete del repositorio, `invalid_status`, defaults PUT y 429; implementar semáforo, resolver su alcance entre workers y documentar/verificar la interfaz.
