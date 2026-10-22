# Estrategia de pruebas — Inventario de dispositivos

> Inventario de cobertura implementada según inspección estática. La cantidad global de pruebas verdes indicada por el usuario no se vuelve a afirmar como ejecución independiente en este documento.

## Alcance y capas

| Capa | Archivo(s) | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_inventory_domain.py` | Reglas de creación con FakeRepo, IPv4 inválida, nombre vacío e ID inexistente al actualizar | Implementado |
| Repositorio | `tests/test_inventory_repository.py` | CRUD del `SQLiteInventoryRepository` usando SQLite en memoria (`:memory:`) | Implementado |
| API | `tests/test_api_inventory.py` | TestClient, CRUD, respuesta vacía, creación, validación de IP y actualización inexistente | Implementado; dependencia sustituida por repositorio en memoria |
| Interfaz | No se encontró suite específica de Inventario | El JavaScript y HTML existen; esta estrategia no afirma cobertura automatizada del frontend | Cobertura automatizada no verificada |

## Matriz de casos implementados

| Caso | Entrada/fixture | Resultado esperado verificado por el test | Prueba | Ejecución en esta auditoría |
|---|---|---|---|---|
| Crear en dominio | FakeRepo y nombre/IP válidos | Asigna ID y conserva el nombre | `test_crear_dispositivo_exitoso` | No ejecutada durante la auditoría documental |
| IP inválida en dominio | `999.999.999.999` | `DomainError` con `invalid_ip` | `test_crear_dispositivo_ip_invalida` | No ejecutada durante la auditoría documental |
| Nombre vacío en dominio | Nombre con espacios | `DomainError` con `invalid_name` | `test_crear_dispositivo_nombre_vacio` | No ejecutada durante la auditoría documental |
| ID inexistente en dominio | Actualización de ID 99 | `DomainError` con `not_found` | `test_actualizar_inexistente` | No ejecutada durante la auditoría documental |
| CRUD SQLite | Repositorio con `:memory:` | Crear/listar, actualizar y eliminar funcionan | `test_crear_y_listar_dispositivo`, `test_actualizar_dispositivo`, `test_eliminar_dispositivo` | No ejecutada durante la auditoría documental |
| API CRUD y lista vacía | TestClient con dependency override a `:memory:` | GET devuelve `[]`; POST 201; GET muestra el registro; PUT 200; DELETE 204; GET vuelve a `[]` | `test_crud_inventario` | No ejecutada durante la auditoría documental |
| IP inválida por API | POST con `999.999.999.999` | HTTP 422 y `error=invalid_ip` | `test_crear_dispositivo_invalido` | No ejecutada durante la auditoría documental |
| Actualizar ID inexistente por API | PUT con ID 99 y body válido | HTTP 422 y `error=not_found` | `test_actualizar_inexistente` en `test_api_inventory.py` | No ejecutada durante la auditoría documental |

## Límites de cobertura observados

- No se encontró test API específico para `invalid_name`, DELETE con ID inexistente, campos extra, tipo incorrecto o campos requeridos ausentes.
- No se encontró un test que compruebe orden descendente con más de un dispositivo.
- No se encontró test que compruebe el efecto de omitir `device_type`, `location` o `notes` durante PUT; según el modelo actual, esos campos toman `""`.
- Los tests API reemplazan `get_inventory_repo` por un repositorio en memoria, evitando usar la base por defecto. Los tests de repositorio también usan `:memory:`.
- La inspección estática no demuestra que los tests hayan sido ejecutados. El usuario informó que el proyecto tiene más de 280 pruebas verdes; esa cifra no se verificó al elaborar este documento.

## Ejecución y última verificación

- **Comando:** no ejecutado durante esta auditoría documental.
- **Entorno:** no verificado dinámicamente.
- **Fecha:** 2026-10-20 (fecha de documentación, no de ejecución de pruebas).
- **Resultado observado:** cobertura identificada leyendo los archivos de prueba; sin resultados dinámicos propios.
- **Pendientes:** verificar los casos de límite de cobertura cuando el usuario autorice una tarea de pruebas.
