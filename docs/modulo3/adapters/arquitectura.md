# Arquitectura — Estado de adaptadores

> Arquitectura objetivo; no describe implementación existente. Los componentes y rutas son destino para una fase de implementación autorizada.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/adapters.py` | Recibir un `AdaptersRunner` inyectado, validar estructura de resultados y devolver datos normalizados | Interfaz del runner; no importa psutil, FastAPI ni el navegador |
| Runner/infraestructura | Adaptador de infraestructura | Ejecutar `psutil.net_if_stats()` y construir objetos estructurados por adaptador | `psutil` |
| API | Ruta GET `/api/v1/tools/adapters/execute` y modelos | Exponer consulta sin body, aplicar semáforo y serializar respuesta | FastAPI/Pydantic, dominio y runner |
| Interfaz | Pendiente de integración | Mostrar lista de adaptadores con estado, velocidad, MTU y multicast | API y recursos locales |
| Pruebas | Archivos a determinar al implementar | Verificar adaptación de datos psutil, dominio y contrato HTTP | Pytest y dobles de prueba |

## Flujo principal

1. El cliente solicita `GET /api/v1/tools/adapters/execute` sin parámetros ni body.
2. La ruta adquiere uno de los cinco permisos del semáforo.
3. El `AdaptersRunner` consulta `psutil.net_if_stats()` para obtener el estado, velocidad, MTU y soporte de multicast de cada adaptador.
4. El runner construye objetos estructurados con `name`, `is_up`, `speed_mbps`, `mtu` e `is_multicast`.
5. El dominio valida la forma y las invariantes acordadas, sin importar psutil ni interpretar datos del sistema operativo.
6. La API devuelve el resultado y libera el semáforo en todos los caminos.

## Adaptación y normalización

- El runner itera sobre los elementos devueltos por `psutil.net_if_stats()` usando el nombre de interfaz como clave.
- `is_up` se deriva del campo de estado (`.isup`) de las estadísticas.
- `speed_mbps` se toma del campo de velocidad en Mbps; si el sistema no informa valor, se almacena `0`.
- `mtu` se toma del campo correspondiente de las estadísticas.
- `is_multicast` se deriva del campo de banderas de las estadísticas, cuando esté disponible en la versión de `psutil` instalada.
- No se leen direcciones IP ni DNS en esta herramienta; la respuesta no incluye esos campos.

## Seguridad, recursos y errores

- La operación es de solo lectura, pero expone información física de adaptadores del servidor.
- No hay datos del cliente que se incorporen a una operación del sistema operativo.
- No guardar consultas ni resultados en persistencia.
- La respuesta pública no debe exponer excepciones, rutas ni detalles internos de psutil.
- El mapeo de fallos de psutil y el sobre HTTP deben seguir el contrato común que se apruebe para el Módulo 3; no asumir que DEC-012, limitado al Módulo 1, fija automáticamente todos estos casos.

## Concurrencia y evolución

La capa API usará `asyncio.Semaphore(5)` y se desplegará con un solo worker de Uvicorn para que el límite sea global. Varios workers tendrían semáforos independientes. La conducta al agotarse los cinco permisos (espera o HTTP 429) no quedó definida.

La dependencia `psutil` queda detrás del runner. Esto reduce el acoplamiento del dominio al sistema operativo y permite sustituir o adaptar las fuentes si cambia la plataforma admitida.

## Decisiones aprobadas y referencias

- [Registro de decisiones](decision-log.md), DEC-017.
- [Catálogo fundacional](../../fundacional/catalogo.md), herramienta 15.
- [Arquitectura de Información de interfaces](../../modulo3/interfaces/arquitectura.md), patrón de consulta local y separación de infraestructura.