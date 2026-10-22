# Requisitos — Generador de informes de diagnóstico

> Estado: alcance aprobado para la herramienta 21. El catálogo fundacional la marca pendiente de desarrollo e integración; este documento no afirma que esté implementada.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 5, herramienta 21.
- **Propósito:** generar un informe estructurado de un diagnóstico de red a partir de datos ingresados por el usuario.
- **Incluye:** recibir título, autor, fecha, hallazgos y conclusión opcional; producir un string en Markdown listo para copiar.
- **No incluye:** generar PDF o imágenes, consultar red, acceder al sistema operativo ni persistir informes.
- **Formato de salida:** Markdown como texto plano.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| REP-F-001 | Recibir los datos del informe. | `title`, `author`, `findings`; `date` opcional y `conclusion` opcional. Cada hallazgo contiene `step` y `result`. | El dominio recibe una estructura validable sin depender del transporte HTTP. | Aprobado |
| REP-F-002 | Validar los campos mínimos. | `title` no vacío y lista `findings` no vacía. | Una entrada que no cumpla estas condiciones se rechaza. | Aprobado |
| REP-F-003 | Asignar fecha cuando no se envía. | `date` omitida. | Se usa la fecha de hoy. | Aprobado; formato y zona horaria pendientes |
| REP-F-004 | Generar el reporte. | Datos válidos. | La respuesta contiene `report_markdown`, un string con el reporte Markdown estructurado. | Aprobado; estructura exacta propuesta |
| REP-F-005 | Incluir una conclusión cuando se suministra. | `conclusion` opcional. | El texto de conclusión se incorpora al reporte si está presente. | Aprobado |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| REP-NF-001 | Arquitectura | El dominio manipula estructuras y strings sin persistencia, red ni sistema operativo. | El cálculo del reporte es puro y determinista dado el mismo contenido y fecha. | Aprobado |
| REP-NF-002 | Dependencias | La salida es Markdown de texto; no se agregan dependencias pesadas para PDF o imágenes. | El flujo no genera documentos binarios ni depende de conversores externos. | Aprobado |
| REP-NF-003 | Concurrencia | La capa API usa `asyncio.Semaphore(5)`. | Las solicitudes de generación pasan por el semáforo de cinco permisos. | Aprobado; conducta de saturación pendiente |

## Criterios de aceptación

- Un request con título y al menos un hallazgo produce `report_markdown`.
- Si se omite `date`, el informe incorpora la fecha actual según la política de fecha que se defina.
- Si se proporciona `conclusion`, queda incluida; si no, no se inventa una conclusión.
- Un título vacío o una lista `findings` vacía se rechaza.
- Cada hallazgo contiene `step` y `result`.
- El resultado se puede copiar como Markdown en texto plano; no se genera PDF ni imagen.

## Fuentes y pendientes

- **Decisiones aplicables:** [REP-DEC-01 y REP-DEC-02](decision-log.md).
- **Fuente de alcance:** [catálogo fundacional, herramienta 21](../../fundacional/catalogo.md).
- **Pendiente de aprobación o investigación:** formato exacto y zona horaria de `date`; si `author`, `step`, `result` deben ser no vacíos; estructura exacta del Markdown; política para caracteres Markdown ingresados; códigos HTTP de validación y saturación del semáforo.
