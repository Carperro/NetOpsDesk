# Contrato de API — Generador de informes de diagnóstico

> Contrato objetivo de la herramienta 21, pendiente de implementación e integración.

## Operación: generar informe

- **Método y ruta:** `POST /api/v1/tools/report-generator/generate`
- **Propósito:** transformar los datos de un diagnóstico en un informe Markdown de texto plano.
- **Content-Type:** `application/json`.

### Solicitud

```json
{
  "title": "Diagnóstico de red - Oficina Central",
  "author": "Nicolás",
  "findings": [
    {
      "step": "Ping a 8.8.8.8",
      "result": "Exitoso, latencia 15ms"
    },
    {
      "step": "DNS a google.com",
      "result": "Resuelve correctamente a 142.250.78.142"
    }
  ],
  "conclusion": "La red funciona correctamente."
}
```

| Campo | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| `title` | string | Sí | No puede estar vacío. |
| `author` | string | No | Nombre del técnico; si se omite, el backend usa `Anónimo`. |
| `date` | string | No | Fecha del informe; si se omite, el backend genera la fecha actual en formato ISO 8601 `YYYY-MM-DD`. |
| `findings` | array de objetos | Sí | No puede estar vacío; cada objeto contiene `step` y `result`. |
| `findings[].step` | string | Sí | Paso o actividad del diagnóstico. |
| `findings[].result` | string | Sí | Resultado del paso. |
| `conclusion` | string | No | Texto de cierre opcional. |

### Respuesta correcta

- **Estado:** HTTP `200 OK` para una solicitud válida.
- **Esquema:** objeto con el único campo `report_markdown`.

```json
{
  "report_markdown": "# Diagnóstico de red - Oficina Central\n\n**Técnico:** Nicolás\n**Fecha:** 2026-10-20\n\n## Hallazgos\n\n### Ping a 8.8.8.8\nExitoso, latencia 15ms\n\n### DNS a google.com\nResuelve correctamente a 142.250.78.142\n\n## Conclusión\nLa red funciona correctamente."
}
```

La estructura del string es contractual: `# {title}`, metadatos `**Técnico:** {author}` y `**Fecha:** {date}`, `## Hallazgos`, cada hallazgo como `### {step}` seguido por `{result}`, y `## Conclusión` seguido por el texto cuando se proporciona `conclusion`. Se separan los bloques con líneas en blanco. Si `author` se omite, se usa `Anónimo`; si `date` se omite, el backend genera la fecha actual como `YYYY-MM-DD`. `report_markdown` es texto plano listo para copiar; este endpoint no devuelve HTML, PDF ni imágenes.

### Errores

| HTTP | Código `error` | Cuándo ocurre | Estado |
|---|---|---|---|
| 422 | `missing_title` | `title` vacío | Error de validación del request. |
| 422 | `empty_findings` | `findings` está vacío | Error de validación del request. |
| 422 | `missing_finding_fields` | Un hallazgo no contiene `step` o `result` | Error de validación del request. |
| 429 | `too_many_requests` | Se agotaron los cinco permisos del semáforo | La solicitud se rechaza. |

No se asume automáticamente que DEC-012, definido para el Módulo 1, rija el Módulo 5. Cuando se formalice, los errores públicos deben incluir mensajes pertinentes en español y no exponer detalles internos.

## Concurrencia

La ruta usa `asyncio.Semaphore(5)` y responde HTTP `429` con `too_many_requests` cuando se agotan los permisos. El semáforo limita concurrencia dentro de su proceso/event loop; no coordina procesos distintos.

## Compatibilidad y verificación

- **OpenAPI:** operación POST JSON; request con hallazgos estructurados y response `{ "report_markdown": "..." }`.
- **Pruebas de contrato:** pendientes de implementación; deben verificar campos requeridos/opcionales, defaults, estructura exacta de salida en texto y cada código/status de error.
- **Cambios incompatibles o pendientes:** no hay decisiones de contrato pendientes en este documento; la implementación y sus pruebas aún deben realizarse.
