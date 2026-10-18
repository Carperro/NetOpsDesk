# Estrategia de pruebas — [Nombre de la herramienta]

> Diferenciar cobertura implementada de cobertura prevista. Esta plantilla no significa que las pruebas se hayan ejecutado.

## Alcance y capas

| Capa | Archivo(s) | Qué verifica | Estado |
|---|---|---|---|
| Dominio | [ruta] | [reglas puras e invariantes] | [implementado/pendiente] |
| API | [ruta] | [estados, esquema, errores y límites HTTP] | [implementado/pendiente] |
| Interfaz/integración | [ruta o procedimiento] | [flujo crítico, estados y presentación segura] | [implementado/pendiente] |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| [ID o caso] | [entrada] | [valor/estado/error] | [test o procedimiento] | [no ejecutado/pasó/falló; fecha y evidencia] |

Incluir casos normales, límites, entradas inválidas, errores, recursos y seguridad pertinentes al alcance. Identificar la fuente independiente de los resultados esperados cuando corresponda.

## Ejecución y última verificación

- **Comando:** `[comando real]`
- **Entorno:** [Python/dependencias relevantes]
- **Fecha:** [AAAA-MM-DD]
- **Resultado observado:** [recolectadas/pasadas/fallidas/omitidas; enlace o salida]
- **Pendientes:** [casos no implementados o verificaciones dinámicas]
