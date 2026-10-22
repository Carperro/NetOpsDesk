# Estrategia de pruebas — Catálogo de puertos y protocolos

> Cobertura prevista para una herramienta pendiente de implementación. No se afirma que existan o se hayan ejecutado pruebas.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_port_catalog_domain.py` | Tamaño mínimo del dataset y reglas de filtrado | Pendiente |
| API | `tests/test_api_port_catalog.py` | Parámetro opcional, esquema de respuesta y estado HTTP | Pendiente |
| Interfaz/integración | Pruebas frontend por definir | Búsqueda y presentación de resultados/vacío | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Dataset mínimo | Sin filtro | Al menos 20 registros locales | Dominio | Pendiente; no ejecutado |
| Consulta por puerto | `80` | Coincidencia HTTP en TCP según dataset | Dominio/API | Pendiente; no ejecutado |
| Consulta por servicio | `http` y `HTTP` | Mismos registros coincidentes | Dominio/API | Pendiente; no ejecutado |
| Coincidencia parcial | `HTT` | Incluye servicios cuyos nombres contienen la consulta | Dominio | Pendiente; no ejecutado |
| Catálogo completo | Consulta omitida y cadena vacía | Se devuelve el dataset completo | Dominio/API | Pendiente; no ejecutado |
| Sin resultados | Texto que no aparece en los registros | HTTP 200 con `ports: []` | API | Pendiente; no ejecutado |
| Forma del registro | Resultado con coincidencia | Cada elemento incluye `port`, `protocol`, `service` y `description` con tipos acordados | API | Pendiente; no ejecutado |
| Semáforo | Solicitudes concurrentes | Verificar máximo cinco; probar conducta de saturación cuando se defina | API | Pendiente; política de saturación abierta |

Los valores esperados para búsqueda deben derivarse del dataset versionado incluido en el dominio y de las reglas de filtrado aprobadas. La corrección de números de puerto y asociaciones de servicio deberá verificarse contra las fuentes que se seleccionen para el dataset; aún no se fijó una fuente normativa para su contenido.

## Ejecución y última verificación

- **Comando:** No ejecutado; esta tarea solo crea documentación.
- **Entorno:** No aplica a la auditoría documental.
- **Fecha:** 2026-10-20.
- **Resultado observado:** No se ejecutaron pruebas.
- **Pendientes:** implementar la herramienta y las pruebas; elegir fuentes de los registros y cerrar las decisiones de búsqueda, errores y saturación.
