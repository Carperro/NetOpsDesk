# Arquitectura — Asistente de resolución de problemas

> Estado: arquitectura objetivo para la herramienta 22. El catálogo la marca pendiente de desarrollo e integración; las ubicaciones descritas son destino, no componentes existentes.

## Componentes y responsabilidades

| Capa/componente | Ubicación | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/troubleshooter.py` | Contener `SYMPTOM_DATABASE` y devolver los datos del síntoma solicitado | Biblioteca estándar; sin runner, FastAPI, base de datos, red ni sistema operativo |
| API | Ruta y modelos por definir al implementar | Recibir el identificador, invocar el dominio y serializar la respuesta | FastAPI/Pydantic y dominio |
| Interfaz | Integración frontend por definir | Permitir elegir un síntoma y mostrar causas y pasos | API y recursos locales |
| Pruebas | Archivos por definir al implementar | Verificar catálogo, consulta de dominio y contrato HTTP | Pytest y cliente de API |

## Flujo principal

1. La interfaz solicita `GET /api/v1/tools/troubleshooter/symptoms/{symptom_id}` sin cuerpo.
2. La ruta tramita la operación bajo `asyncio.Semaphore(5)`.
3. La API pasa el identificador al dominio; no hay entrada que se use para construir comandos ni consultas externas.
4. El dominio busca el identificador en `SYMPTOM_DATABASE`; si no existe, lanza `DomainError` con código `invalid_symptom`.
5. La API responde con `symptom_id`, `symptom_name` y la lista `causes`, cuyas causas contienen `cause` y `steps`.
6. La interfaz presenta los textos como contenido, no como HTML.

El handler global traduce `DomainError(invalid_symptom)` a HTTP `422`. Si el semáforo está agotado, la API rechaza la solicitud con HTTP `429` y código `too_many_requests`.

## Catálogo de síntomas

El dominio mantiene un diccionario estático llamado `SYMPTOM_DATABASE`. Debe incluir como mínimo:

| Identificador | Nombre descriptivo |
|---|---|
| `sin_internet` | Sin acceso a internet |
| `internet_lento` | Latencia alta o pérdida de paquetes |
| `dns_falla` | No resuelve nombres de dominio |

Cada entrada incluye al menos tres causas posibles. Cada causa contiene un título y una lista ordenada de pasos de solución como strings. La selección y redacción concreta de causas y pasos debe ser consistente con el alcance técnico que se apruebe; no se considera definida por esta estructura.

## Límites y errores

- **Validación en interfaz:** limita la selección a los síntomas disponibles, pero no reemplaza la validación de la API.
- **Validación API/dominio:** el dominio solo devuelve identificadores presentes en el catálogo; un identificador desconocido produce `DomainError` con código `invalid_symptom`, traducido por el handler global a HTTP 422.
- **Errores y advertencias:** la saturación del semáforo produce HTTP 429 con código `too_many_requests`. Los detalles públicos deben estar en español y no exponer información interna.
- **Recursos y seguridad:** el catálogo es estático y acotado; no se ejecutan comandos, no se hacen conexiones de red y no se guarda información. La interfaz trata los datos como texto no confiable y no los inserta como HTML.

## Concurrencia y evolución

La API usa `asyncio.Semaphore(5)` y responde HTTP 429 con `too_many_requests` cuando no hay permisos disponibles. El semáforo limita dentro de su proceso/event loop; el alcance global entre procesos requiere un único worker o coordinación compartida, aspecto de despliegue que no queda fijado por esta decisión.

La consulta directa al dominio es suficiente para el catálogo local. No se añade una capa de servicio o persistencia mientras no exista una necesidad concreta que la justifique.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** catálogo estático `SYMPTOM_DATABASE` en el dominio, sin runner; tres identificadores mínimos y al menos tres causas por síntoma; error `invalid_symptom` como HTTP 422 y saturación del semáforo como HTTP 429 `too_many_requests` (TRB-DEC-01 y TRB-DEC-02).
- **Alternativas descartadas:** consultas automáticas a red o sistema operativo; no forman parte del árbol estático aprobado.
- **Dependencias de plataforma/conectividad:** ninguna.
- **Límites que permiten evolución futura:** conservar los datos y la consulta en el dominio permite cambiar el transporte o la interfaz sin acoplar el contenido a FastAPI.

## Referencias

- [Requisitos](requisitos.md), [contrato API](api-contracts.md), [decisiones](decision-log.md) y [estrategia de pruebas](test-strategy.md).
- [Catálogo fundacional, herramienta 22](../../fundacional/catalogo.md).
