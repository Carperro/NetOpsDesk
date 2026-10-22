# Estrategia de pruebas — Información de interfaces de red

## Estado

Estrategia prevista para la futura implementación. No afirma que existan pruebas específicas de interfaces ni que se hayan ejecutado. La cifra global de 258 tests indicada en la solicitud no se verificó durante esta tarea.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Runner/infraestructura | A determinar al implementar | Adaptación de `net_if_addrs()` y `net_if_stats()` a objetos por interfaz | Pendiente |
| Dominio | A determinar al implementar | Validación de estructura y conservación de campos | Pendiente |
| API | A determinar al implementar | GET sin body, esquema, concurrencia y errores | Pendiente |
| Interfaz/integración | A determinar con el frontend | Presentación de lista, estado, datos opcionales y errores | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Sin interfaces | Runner falso devuelve mapas vacíos | `interfaces: []` | Test unitario/API | Pendiente/no ejecutado |
| Interfaz completa | Un nombre con MAC, IPv4, máscara y stats | Se devuelven los seis campos con tipos acordados | Test de runner y contrato | Pendiente/no ejecutado |
| Múltiples interfaces | Varias interfaces con estados distintos | Cada resultado conserva asociación por nombre; sin mezclar datos | Test unitario de runner | Pendiente/no ejecutado |
| Sin IPv4/MAC | Interfaz solo con otros tipos de dirección | Resultado sigue la semántica de null/omisión aprobada | Test unitario | Pendiente; política por definir |
| Varias IPv4 | Interfaz con más de una dirección IPv4 | Selección o representación según decisión aprobada | Test unitario | Pendiente; política por definir |
| Interfaz down | Stats con `isup == false` | `is_up: false` | Test unitario/API | Pendiente/no ejecutado |
| Velocidad desconocida | Stats con `speed == 0` o valor ausente | Resultado según representación aprobada | Test unitario | Pendiente; política por definir |
| Fallo de psutil | Runner produce una excepción controlada | No fabricar éxito ni exponer detalles internos | Test API | Pendiente; status/código por definir |
| GET sin body | Request al endpoint sin payload | Request válido y respuesta según contrato | Test de contrato | Pendiente/no ejecutado |
| Concurrencia | Cinco llamadas simultáneas y una adicional | Límite según política de workers y saturación | Test API | Pendiente; política por definir |
| Aislamiento del dominio | Fake runner inyectado | Dominio no importa psutil ni consulta el sistema real | Test estático/unitario | Pendiente/no ejecutado |

## Datos esperados independientes

Usar dobles de `psutil.net_if_addrs()` y `psutil.net_if_stats()` con fixtures declarados, sin depender del adaptador de red real de CI. Verificar por separado la asociación entre dirección MAC/IPv4 y estadísticas usando nombres de interfaz conocidos del fixture.

## Ejecución y última verificación

- **Comando:** No ejecutado en esta tarea.
- **Entorno:** No se verificó dinámicamente.
- **Fecha:** 2026-10-20 (fecha de documentación; no es fecha de ejecución de pruebas).
- **Resultado observado:** Sin resultados de pruebas específicos de la herramienta 11.
- **Pendientes:** implementar pruebas junto con la herramienta y cerrar las decisiones de cardinalidad, errores y concurrencia.
