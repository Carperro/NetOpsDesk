# Contrato de API — [Nombre de la herramienta]

> Registrar el contrato público verificado. Mantener nombres, códigos y estados HTTP coherentes con la implementación y el contrato común.

## Operación: [nombre]

- **Método y ruta:** `[METHOD] /api/v1/...`
- **Propósito:** [resultado de la operación]
- **Content-Type:** [tipo aceptado]

### Solicitud

```json
{}
```

| Campo | Tipo | Requerido | Restricciones y semántica |
|---|---|---|---|
| [campo] | [tipo] | [sí/no] | [restricciones] |

### Respuesta correcta

- **Estado:** [código]
- **Esquema:** [campos y semántica]

```json
{}
```

### Errores

| HTTP | Código `error` | Cuándo ocurre | `detail`/mensaje esperado |
|---|---|---|---|
| [código] | [código estable] | [condición] | [mensaje en español] |

Los errores siguen el sobre común `{ "error": "<código>", "detail": "<mensaje>" }`, según `docs/modulo1/api-contracts.md` y las decisiones vigentes.

## Compatibilidad y verificación

- **OpenAPI:** [operación y modelos expuestos; anotar diferencias observadas].
- **Pruebas de contrato:** [archivos y casos; no afirmar ejecución sin evidencia].
- **Cambios incompatibles o pendientes:** [detalle o «Ninguno»].
