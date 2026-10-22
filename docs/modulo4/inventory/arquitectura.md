# Arquitectura — Inventario de dispositivos

> Estado: descripción contrastada con el código disponible de dominio, repositorio, API y frontend.

## Componentes y responsabilidades

| Capa/componente | Ubicación | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/inventory.py` | Validar nombre e IP, aplicar reglas de negocio y devolver objetos de datos estructurados | Biblioteca estándar (`ipaddress`); recibe el repositorio inyectado |
| Repositorio | `src/netops_desk/repositories/inventory_repository.py` | Interfaz e implementación SQLite para persistencia de dispositivos | Módulo estándar `sqlite3`; el dominio recibe el repositorio por inyección |
| API | `src/netops_desk/api/models/inventory.py`, `src/netops_desk/api/routes/inventory.py` | Validar entrada, inyectar repositorio, mapear operaciones CRUD y serializar respuestas | FastAPI/Pydantic, dominio y repositorio |
| Interfaz | `src/netops_desk/static/tools/inventory.html`, `src/netops_desk/static/js/inventory.js`, `src/netops_desk/static/css/inventory.css` | Crear, editar, eliminar y listar dispositivos mediante el API | API y recursos locales |
| Pruebas | `tests/test_inventory_domain.py`, `tests/test_inventory_repository.py`, `tests/test_api_inventory.py` | Validaciones del dominio con FakeRepo, CRUD SQLite en memoria y contrato HTTP con dependency override | Pytest y TestClient |

## Flujo principal

1. El cliente envía una solicitud HTTP con los datos del dispositivo (nombre, IP, tipo, ubicación, observaciones).
2. El modelo de API valida la estructura del cuerpo contra el esquema Pydantic.
3. FastAPI obtiene el repositorio mediante `get_inventory_repo()`; por defecto crea `SQLiteInventoryRepository()` con la ruta relativa `netops.db`.
4. La ruta llama al dominio, que valida IPv4 y nombre no vacío; las reglas no dependen de FastAPI.
5. El dominio opera mediante la interfaz `InventoryRepository`; la implementación SQLite ejecuta SQL parametrizado y devuelve los resultados.
6. La API serializa la respuesta y la devuelve al cliente.

## Límites y errores

- **Validación en interfaz:** la interfaz puede repetir validaciones para mejorar la experiencia de usuario, pero la API y el dominio protegen sus propios límites.
- **Validación API/dominio:** la IP se valida como IPv4 válida; el nombre debe estar presente y no vacío. Los errores del dominio se traducen en la capa API.
- **Errores y advertencias:** `422 invalid_name` para nombre vacío/blanco; `422 invalid_ip` para IPv4 inválida; `422 not_found` para PUT/DELETE sobre un ID inexistente. `name` ausente se traduce por validación Pydantic a `422 missing_field`.
- **Recursos y seguridad:** la base de datos es local y no se expone por esta herramienta. Evidencia del estado revisado: `netops.db` está rastreada por Git (`git ls-files`) y no tiene regla en `.gitignore`; la afirmación previa de que está ignorada no coincide con el repositorio. No se modificó el archivo de base ni la configuración Git en esta tarea.

## Base de datos

Tabla `devices`:

| Columna | Tipo | Semántica |
|---|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Identificador único del dispositivo |
| `name` | TEXT NOT NULL | Nombre recortado y no vacío |
| `ip_address` | TEXT NOT NULL | Dirección IPv4 validada por el dominio |
| `device_type` | TEXT NOT NULL | Cadena libre; default de API `""` |
| `location` | TEXT | Cadena libre; default de API `""` |
| `notes` | TEXT | Cadena libre; default de API `""` |

La base de datos se crea automáticamente si no existe mediante `sqlite3.connect("netops.db")` y `CREATE TABLE IF NOT EXISTS`. El nombre es relativo al directorio de trabajo del proceso, no se fija a la raíz del repositorio. La conexión usa `check_same_thread=False` y `sqlite3.Row`; el repositorio no usa ORM. El repositorio de pruebas recibe `db_path=":memory:"`.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** DEC-018, registrada en el decision log local; SQLite nativo y patrón Repository, sin ORM.
- **Alternativas descartadas:** uso de SQLAlchemy/ORM (descartado: añade una dependencia innecesaria para una persistencia local sencilla); base de datos en memoria permanente (descartado: no cumple el requisito de persistencia entre ejecuciones).
- **Dependencias de plataforma/conectividad:** depende de SQLite de la biblioteca estándar y del permiso de escritura en el directorio de trabajo.
- **Límites que permiten evolución futura:** el repositorio se accede mediante una interfaz inyectada, por lo que la implementación de persistencia puede cambiarse sin afectar al dominio.
