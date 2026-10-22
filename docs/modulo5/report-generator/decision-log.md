# Registro de decisiones — Generador de informes de diagnóstico

Este registro contiene decisiones específicas de la herramienta 21 aprobadas por el usuario. La existencia de este documento no implica que la herramienta esté implementada.

## Decisiones aprobadas

### REP-DEC-01 — Generación pura de Markdown

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Se necesita entregar un informe portable sin incorporar dependencias pesadas ni operaciones externas.
- **Decisión:** El dominio `netops_desk/report_generator.py` recibe estructuras de datos y devuelve un string de reporte Markdown. No genera PDF ni imágenes y no usa base de datos, red ni sistema operativo.
- **Motivo:** Limitar la herramienta a composición de texto y mantener la lógica desacoplada de infraestructura.
- **Alternativas:** PDF e imágenes; descartados para evitar dependencias pesadas y ampliar el alcance.
- **Consecuencias:** La interfaz recibe texto listo para copiar. La estructura aprobada se registra en REP-DEC-03.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 21.

### REP-DEC-02 — Entradas mínimas y concurrencia

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Definir los datos necesarios para generar un informe y limitar solicitudes concurrentes.
- **Decisión:** Recibir `title`, `author` opcional (default `Anónimo`), `findings` (objetos con `step` y `result`), `date` opcional (default: fecha actual generada por backend en formato ISO 8601 `YYYY-MM-DD`) y `conclusion` opcional. Rechazar título o lista de hallazgos vacíos. La capa API usa `asyncio.Semaphore(5)`.
- **Motivo:** Asegurar que cada reporte tenga tema y contenido diagnóstico, con fecha y cierre opcional.
- **Alternativas:** No registradas.
- **Consecuencias:** El contrato define los defaults; la implementación debe respetarlos. Los errores y la saturación se detallan en REP-DEC-05.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 21.

### REP-DEC-03 — Estructura del reporte Markdown

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** La herramienta necesita una salida consistente y lista para copiar.
- **Decisión:** El reporte usa, en este orden, `# {title}`, `**Técnico:** {author}`, `**Fecha:** {date}`, `## Hallazgos`, un bloque `### {step}` seguido de `{result}` por cada elemento, y `## Conclusión` con el texto si se proporciona. Los hallazgos conservan el orden de entrada y los bloques se separan con líneas en blanco.
- **Motivo:** Fijar el formato contractual de salida y evitar presentaciones divergentes entre clientes.
- **Consecuencias:** `report_markdown` contiene Markdown como texto plano; no implica renderizado HTML.

### REP-DEC-04 — Defaults de autor y fecha

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Autor y fecha pueden omitirse en el request.
- **Decisión:** `author` es opcional y usa `Anónimo` si se omite. `date` es opcional y el backend genera la fecha actual en formato ISO 8601 `YYYY-MM-DD` si se omite.
- **Motivo:** Permitir generar informes con metadatos útiles aun cuando el cliente no los envíe.
- **Consecuencias:** La respuesta renderizada incluye los valores aplicados; la entrada `date` explícita se conserva como fecha del informe.

### REP-DEC-05 — Errores de validación y saturación

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** El contrato debe identificar entradas no válidas y solicitudes que no pueden admitirse por concurrencia.
- **Decisión:** `missing_title`, `empty_findings` y `missing_finding_fields` responden HTTP 422. El semáforo `asyncio.Semaphore(5)` rechaza solicitudes al agotarse con HTTP 429 y código `too_many_requests`.
- **Motivo:** Proporcionar fallos contractuales estables para validación y control de concurrencia.
- **Consecuencias:** La interfaz debe presentar mensajes pertinentes en español para estos errores; las pruebas de API deben cubrir los códigos y estados.

## Pendientes de decisión

- Definir si `step` y `result` deben ser no vacíos y cómo tratar espacios en blanco.
- Definir cómo conservar o escapar caracteres Markdown/HTML ingresados por el usuario.
