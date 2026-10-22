# Arquitectura — Generador de informes de diagnóstico

> Estado: arquitectura objetivo para la herramienta 21. El catálogo la marca pendiente de desarrollo e integración; las ubicaciones descritas son destino y no componentes existentes.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/report_generator.py` | Validar datos de negocio y transformar la estructura del informe en un string Markdown | Biblioteca estándar; sin FastAPI, base de datos, sistema operativo ni red |
| Modelo y ruta API | Por definir al implementar | Validar el request, aplicar defaults, invocar dominio y devolver resultado | FastAPI/Pydantic y dominio |
| Interfaz | Integración frontend por definir | Capturar datos, mostrar el reporte como texto y permitir copiarlo | API y recursos locales |
| Pruebas | Archivos por definir al implementar | Verificar validación, composición de Markdown, API y copia | Pytest y cliente de API |

## Flujo principal

1. La interfaz envía `POST /api/v1/tools/report-generator/generate` con título, autor, hallazgos y campos opcionales.
2. La API valida la estructura; si falta `author`, aplica `Anónimo`, y si falta `date`, genera la fecha actual en formato ISO 8601 `YYYY-MM-DD`.
3. La ruta ejecuta la operación bajo `asyncio.Semaphore(5)` y llama al dominio con datos estructurados. Si el semáforo está agotado, rechaza la solicitud con HTTP 429 y `too_many_requests`.
4. El dominio verifica las invariantes de negocio y compone el string Markdown; no accede a persistencia ni a servicios externos.
5. La API devuelve `{ "report_markdown": "..." }`.
6. La interfaz muestra el string como texto y, cuando el usuario lo solicita, lo copia al portapapeles.

## Estructura de reporte aprobada

El dominio genera el reporte con esta estructura y en este orden, separando los bloques con líneas en blanco:

```markdown
# {title}

**Técnico:** {author}
**Fecha:** {date}

## Hallazgos

### {step}
{result}

## Conclusión
{conclusion}
```

Se repite el bloque `### {step}` y `{result}` por cada hallazgo, conservando el orden de entrada. `author` usa `Anónimo` si se omite; `date` usa la fecha actual generada por el backend en formato `YYYY-MM-DD` si se omite. La sección `## Conclusión` se incluye cuando se proporciona `conclusion`.

## Límites y errores

- **Validación en interfaz:** puede guiar la captura, pero no sustituye la validación API/dominio.
- **Validación API/dominio:** `title` y `findings` no pueden estar vacíos; cada hallazgo debe incluir `step` y `result`. El contrato asigna `missing_title`, `empty_findings` y `missing_finding_fields` a HTTP 422.
- **Errores y advertencias:** si se agotan los cinco permisos del semáforo, la API rechaza la solicitud con HTTP 429 y `too_many_requests`. No se presume que DEC-012, limitado al Módulo 1, defina el resto del contrato transversal del Módulo 5.
- **Recursos y seguridad:** tratar todos los campos como texto no confiable. La interfaz presenta `report_markdown` como texto (por ejemplo, `textContent` o un área de texto), no como HTML. Si se agrega una vista renderizada de Markdown, sanitización y reglas contra HTML embebido requieren una decisión específica.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** transformación pura en `netops_desk/report_generator.py`; salida Markdown en string con la estructura de este documento; fecha actual en formato `YYYY-MM-DD` y autor `Anónimo` como defaults; errores de validación 422 y saturación 429; sin PDF/imágenes, base de datos, red ni sistema operativo; semáforo API de cinco permisos (REP-DEC-01 a REP-DEC-05).
- **Alternativas descartadas:** generación de PDF o imágenes, por alcance y para evitar dependencias pesadas.
- **Dependencias de plataforma/conectividad:** ninguna para generar el texto.
- **Límites que permiten evolución futura:** mantener la generación independiente del transporte permite reutilizarla desde otra interfaz sin introducir dependencias de presentación en el dominio.

## Referencias

- [Requisitos](requisitos.md), [contrato API](api-contracts.md), [decisiones](decision-log.md) y [estrategia de pruebas](test-strategy.md).
- [Catálogo fundacional, herramienta 21](../../fundacional/catalogo.md).
