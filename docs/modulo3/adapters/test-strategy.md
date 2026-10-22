# Estrategia de pruebas — Estado de adaptadores

> Estrategia prevista para la futura implementación. No afirma que existan pruebas específicas de adaptadores ni que se hayan ejecutado. La cifra global de tests del proyecto no se verificó durante esta tarea.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Runner/infraestructura | A determinar al implementar | Adaptación de `net_if_stats()` a objetos por adaptador | Pendiente |
| Dominio | A determinar al implementar | Validación de estructura y conservación de campos | Pendiente |
| API | A determinar al implementar | GET sin body, esquema, concurrencia y errores | Pendiente |
| Interfaz/integración | A determinar con el frontend | Presentación de lista, estado, velocidad, MTU y multicast | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Sin adaptadores | Runner falso devuelve mapa vacío | `adapters: []` | Test unitario/API | Pendiente/no ejecutado |
| Adaptador completo | Un nombre con estado, velocidad, MTU y banderas | Se devuelven los cinco campos con tipos acordados | Test de runner y contrato | Pendiente/no ejecutado |
| Múltiples adaptadores | Varios adaptadores con estados distintos | Cada resultado conserva asociación por nombre; sin mezclar datos | Test unitario de runner | Pendiente/no ejecutado |
| Adaptador down | Stats con `isup == false` | `is_up: false` | Test unitario/API | Pendiente/no ejecutado |
| Velocidad desconocida | Stats con `speed == 0` o valor ausente | `speed_mbps: 0` | Test unitario | Pendiente/no ejecutado |
| MTU ausente o cero | Stats sin valor de MTU | `mtu` según representación aprobada | Test unitario | Pendiente; política por definir |
| Multicast no disponible | Stats sin bandera de multicast | `is_multicast` según representación aprobada | Test unitario | Pendiente; política por definir |
| Fallo de psutil | Runner produce una excepción controlada | No fabricar éxito ni exponer detalles internos | Test API | Pendiente; status/código por definir |
| GET sin body | Request al endpoint sin payload | Request válido y respuesta según contrato | Test de contrato | Pendiente/no ejecutado |
| Concurrencia | Cinco llamadas simultáneas y una adicional | Límite según política de workers y saturación | Test API | Pendiente; política por definir |
| Aislamiento del dominio | Fake runner inyectado | Dominio no importa psutil ni consulta el sistema real | Test estático/unitario | Pendiente/no ejecutado |

## Datos esperados independientes

Usar dobles de `psutil.net_if_stats()` con fixtures declarados, sin depender del adaptador de red real de CI. Verificar por separado la asociación de estado, velocidad, MTU y banderas usando nombres de adaptador conocidos del fixture.

## Ejecución y última verificación

- **Comando:** No ejecutado en esta tarea.
- **Entorno:** No se verificó dinámicamente.
- **Fecha:** 2026-10-20 (fecha de documentación; no es fecha de ejecución de pruebas).
- **Resultado observado:** Sin resultados de pruebas específicos de la herramienta 15.
- **Pendientes:** implementar pruebas junto con la herramienta y cerrar las decisiones de errores, concurrencia y soporte de multicast.