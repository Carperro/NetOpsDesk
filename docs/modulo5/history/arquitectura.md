# Arquitectura — Historial de diagnósticos

> Arquitectura objetivo definida para la herramienta 25; no describe componentes implementados.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `netops_desk/history.py` | Coordinar creación, listado, eliminación y limpieza; mantener reglas independientes de SQL y HTTP | Biblioteca estándar y abstracción del repositorio inyectada |
| Repositorio | `netops_desk/repositories/history_repository.py` | Persistir y consultar entradas en `history` dentro de `netops.db` | `sqlite3` estándar; consultas parametrizadas |
| API | Modelos y rutas aún por definir | Validar solicitudes, inyectar repositorio, exponer operaciones y aplicar semáforo | FastAPI/Pydantic, dominio y proveedor de repositorio |
| Interfaz | HTML/CSS/JavaScript aún por definir | Consultar historial, agregar entradas manualmente y borrar entradas o colección | API y recursos locales |
| Pruebas | Archivos aún por definir | Cubrir dominio, repositorio SQLite, contrato HTTP e interfaz | Pytest y SQLite `:memory:` |

## Base de datos

La tabla `history` usa estas columnas:

| Columna | Tipo SQLite | Semántica |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Identificador generado para la entrada |
| `tool_name` | `TEXT` | Nombre de la herramienta; obligatorio en la solicitud |
| `action` | `TEXT` | Acción realizada; obligatoria en la solicitud |
| `result_status` | `TEXT` | Estado o resultado de la acción; la obligatoriedad en la solicitud está pendiente de confirmación |
| `details` | `TEXT` | Detalle; opcional en la solicitud, default de aplicación `""` |
| `created_at` | `TEXT` | Timestamp generado con `datetime.now().isoformat()` |

La base es el archivo SQLite compartido `netops.db`, de acuerdo con DEC-018. El repositorio lista con `ORDER BY created_at DESC, id DESC`, por lo que `id DESC` resuelve empates de timestamp.

## Flujo principal

1. La interfaz envía un POST con los datos de una entrada o solicita consulta/borrado.
2. La API valida el request, obtiene uno de los cinco permisos del semáforo y resuelve el repositorio SQLite por inyección.
3. El dominio aplica las reglas y usa la abstracción del repositorio, sin conocer SQL ni FastAPI.
4. El repositorio ejecuta la operación sobre `history` en `netops.db` y devuelve los datos al dominio.
5. La API serializa la respuesta y la interfaz actualiza la lista o presenta el resultado.

## Límites y errores

- **Validación en interfaz:** puede validar campos para ayudar al usuario; la API debe proteger sus propios límites.
- **Validación API/dominio:** `tool_name` y `action` son requeridos; `details` es opcional y usa `""` si se omite. La obligatoriedad de `result_status` debe confirmarse antes de implementar. Los demás límites de campos siguen pendientes.
- **Errores y advertencias:** ID inexistente al eliminar: HTTP 422 `not_found`. Semáforo agotado: HTTP 429 `too_many_requests`. Los errores de esquema deben alinearse con el contrato común aplicable al Módulo 5.
- **Recursos y seguridad:** usar SQL parametrizado. Limitar los datos operativos de `details` a los flujos autorizados y evitar su escritura en logs innecesarios. No registrar automáticamente datos desde las herramientas 1–24 en esta etapa.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** SQLite nativo mediante `sqlite3`, sin ORM, base compartida y patrón Repository (DEC-018); aislamiento de los dominios 1–24 (DEC-HISTORY-02); tipos, timestamp y orden de la tabla (DEC-HISTORY-03). Ver [registro de decisiones](decision-log.md).
- **Alternativas descartadas:** acoplar los dominios de las herramientas 1–24 a la tabla de historial, para preservar su aislamiento.
- **Dependencias de plataforma/conectividad:** SQLite local; no requiere servicios externos.
- **Límites que permiten evolución futura:** una integración futura podrá enviar registros por la API manteniendo el almacenamiento encapsulado detrás del repositorio.