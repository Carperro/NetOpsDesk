# Contrato común de API — Módulo 1

## Alcance y separación

Este documento define las convenciones transversales de los contratos HTTP del Módulo 1. Cada herramienta conserva en su propio directorio las rutas, campos de solicitud, esquemas de respuesta y códigos específicos.

La lógica de dominio no depende de FastAPI ni de HTTP. Las rutas de API adaptan solicitudes HTTP al dominio y sus resultados a los modelos de respuesta. Los errores de dominio se traducen en la capa API; el dominio no debe producir códigos HTTP.

## Formato de errores

Las respuestas de error usan JSON con estas dos propiedades de tipo cadena:

```json
{
  "error": "<código estable>",
  "detail": "<mensaje legible>"
}
```

Los códigos específicos y los detalles esperados se documentan en el contrato de cada herramienta. Los errores no deben exponer trazas, rutas internas ni detalles sensibles.

## Semántica HTTP común

| Estado | Uso contractual |
|---|---|
| `200` | Operación completada correctamente. |
| `400` | El cuerpo no puede leerse o decodificarse como JSON, conforme a DEC-007. |
| `415` | El tipo de contenido de la solicitud no está admitido. |
| `422` | JSON sintácticamente válido que no cumple el esquema, las reglas de entrada o las invariantes de la operación. Incluye errores de dominio traducidos por la API. |
| `500` | Error inesperado; el detalle público es genérico y no revela información interna. |

Las respuestas para rutas o métodos no admitidos conservan los estados HTTP correspondientes y usan el sobre JSON común cuando la aplicación puede producirlo.

## Estado de conformidad observado

Estado revisado el 2026-10-18: las cuatro herramientas implementadas del Módulo 1 (IPv4/CIDR, Subnetting, VLSM y Overlap) usan el contrato común de DEC-012. Los errores de esquema y de dominio responden HTTP `422`; los tipos de contenido distintos de `application/json` responden HTTP `415`; las excepciones inesperadas responden HTTP `500` con detalle seguro.

Todas las respuestas de error usan `{ "error": "<código>", "detail": "<mensaje>" }`. Los mensajes destinados al usuario se mantienen en español. La interfaz presenta detalles contractuales localizados y usa mensajes propios en español para fallos de conexión o respuestas inesperadas, sin mostrar mensajes técnicos del navegador.
## Contratos por herramienta

- [Calculadora IPv4/CIDR](ipv4-calculator/api-contracts.md)
- [Subnetting IPv4](subnetting/api-contracts.md)
- [Planificador VLSM](vlsm/api-contracts.md)

La documentación específica de Overlap sigue pendiente; hasta que se documente, sus reglas compartidas de errores HTTP se rigen por este contrato común.
