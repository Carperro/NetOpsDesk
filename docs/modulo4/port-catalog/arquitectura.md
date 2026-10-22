# Arquitectura — Catálogo de puertos y protocolos

> Estado: arquitectura objetivo para la herramienta 19. El catálogo la marca pendiente de desarrollo e integración; las ubicaciones descritas son destino, no componentes existentes.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/port_catalog.py` | Mantener el dataset estático y filtrar registros por consulta | Biblioteca estándar; no requiere runner, base de datos, sistema operativo ni red |
| Modelo y ruta API | Modelo/ruta por definir al implementar | Exponer `GET /api/v1/tools/port-catalog/search`, pasar la consulta al dominio y serializar los resultados | FastAPI/Pydantic y dominio |
| Interfaz | Integración frontend por definir | Permitir buscar por puerto o servicio y mostrar los registros | API y recursos locales |
| Pruebas | Archivos por definir al implementar | Verificar dataset, búsqueda, coincidencias parciales y contrato HTTP | Pytest y cliente de API |

## Flujo principal

1. La interfaz envía una solicitud GET con `query` opcional.
2. La ruta API ejecuta la operación bajo `asyncio.Semaphore(5)`.
3. La ruta llama directamente a la función de búsqueda del dominio; no se necesita una capa runner porque no hay integración con el sistema operativo.
4. El dominio normaliza la consulta con `.strip().lower()` y filtra el dataset local estático por número de puerto o servicio con coincidencia parcial.
5. Si la consulta normalizada está vacía, el dominio devuelve todos los registros; si no encuentra coincidencias, devuelve una lista vacía. En ambos casos la API responde HTTP `200 OK` con `{"ports": [...]}`.
6. La interfaz presenta los campos como texto.

## Límites y errores

- **Validación en interfaz:** puede facilitar la entrada, pero no define por sí sola el comportamiento de búsqueda.
- **Validación API/dominio:** `query` es opcional; una consulta vacía representa el listado completo. El contrato no define todavía límite de longitud.
- **Errores y advertencias:** la herramienta no genera `DomainError`; la ausencia de coincidencias es un resultado normal con HTTP `200` y `ports: []`. Cuando el semáforo está agotado, la API responde HTTP `429` con código `too_many_requests`.
- **Recursos y seguridad:** la consulta solo lee datos estáticos locales. No se ejecutan comandos, no se realizan conexiones de red y no se persisten búsquedas.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** dataset estático y filtrado puro en el dominio; búsqueda normalizada con `.strip().lower()`; consulta vacía devuelve todos; sin coincidencias devuelve HTTP 200 con `ports: []`; semáforo API de cinco permisos que responde HTTP 429 `too_many_requests` al agotarse (PORT-DEC-01 y PORT-DEC-02).
- **Alternativas descartadas:** incorporar base de datos, `subprocess` o una consulta a un servicio remoto para el catálogo inicial.
- **Dependencias de plataforma/conectividad:** ninguna para la operación de consulta.
- **Límites que permiten evolución futura:** el dataset puede reemplazarse por otra fuente manteniendo estable la función de consulta y el contrato, cuando una necesidad concreta lo justifique.

## Referencias

- [Requisitos](requisitos.md), [contrato API](api-contracts.md), [decisiones](decision-log.md) y [estrategia de pruebas](test-strategy.md).
- [Catálogo fundacional, herramienta 19](../../fundacional/catalogo.md).
