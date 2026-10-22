# Estrategia de pruebas — Asistente de resolución de problemas

> Cobertura prevista para una herramienta pendiente de implementación. No se afirma que existan o se hayan ejecutado pruebas.

## Alcance y capas

| Capa | Archivo(s) | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_troubleshooter_domain.py` | Síntomas mínimos, cantidad y estructura de causas, búsqueda por ID y orden | Pendiente de implementación |
| API | `tests/test_api_troubleshooter.py` | Ruta GET, parámetro de ruta y esquema de respuesta | Pendiente de implementación |
| Interfaz/integración | Pruebas frontend por definir | Selección de síntoma y presentación segura de causas y pasos | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Catálogo mínimo | Inspección de `SYMPTOM_DATABASE` | Incluye `sin_internet`, `internet_lento` y `dns_falla` | Dominio | Pendiente; no ejecutado |
| Cantidad mínima de causas | Cada síntoma del catálogo | Al menos tres causas por síntoma | Dominio | Pendiente; no ejecutado |
| Forma de causa | Cada causa | Tiene título y lista `steps` de strings | Dominio | Pendiente; no ejecutado |
| Orden de pasos | Síntoma con varios pasos | Se mantiene el orden definido en los datos | Dominio/API | Pendiente; no ejecutado |
| Consulta válida | GET con ID conocido | HTTP 200 y `symptom_id`, `symptom_name`, `causes` | API | Pendiente; no ejecutado |
| ID desconocido | GET con ID no presente | Resultado según política HTTP pendiente de decisión | API | Pendiente; no ejecutado |
| Límite de concurrencia | Solicitudes simultáneas por encima de cinco | Resultado según política de saturación pendiente de decisión | API | Pendiente; no ejecutado |
| Sin efectos externos | Consulta del dominio | No accede a red, base de datos ni sistema operativo | Dominio | Pendiente; no ejecutado |
| Presentación segura | Campos de texto del catálogo | Se presentan como texto, no como HTML interpretado | Frontend | Pendiente; no ejecutado |

Las pruebas de dominio deben contrastar los datos con los requisitos aprobados del catálogo, no con resultados de red. Los contenidos específicos de causas y pasos requieren definición antes de fijar aserciones detalladas.

## Ejecución y última verificación

- **Comando:** No ejecutado; esta tarea documenta la estrategia prevista.
- **Entorno:** No aplica a la documentación de una herramienta aún no implementada.
- **Fecha:** 2026-10-20.
- **Resultado observado:** No se ejecutaron pruebas.
- **Pendientes:** implementar dominio, API e interfaz; aprobar contenidos de síntomas y políticas HTTP pendientes; crear y ejecutar la cobertura descrita.
