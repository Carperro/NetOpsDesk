# Estrategia de pruebas — Visor de tabla de rutas

> Cobertura prevista para implementación futura. La existencia de pruebas de Route Analyzer no significa que la herramienta 14 esté verificada.

## Alcance y capas

| Capa | Archivo(s) | Qué verifica | Estado |
|---|---|---|---|
| Dominio | Por determinar; se espera `tests/test_route_table_domain.py` | Parseo de filas, campos, métrica, filas `On-link` y salidas localizadas | Pendiente |
| API | Por determinar; se espera `tests/test_api_route_table.py` | GET sin body, esquema de respuesta, timeout, errores y semáforo | Pendiente |
| Interfaz/integración | Prueba estática/frontend por determinar | Tabla, estado vacío/error y renderizado seguro | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Ruta IPv4 válida | Línea con destino, máscara, gateway, interfaz y métrica | Una ruta con cuatro direcciones IPv4 y métrica entera correcta | Unit test con salida fixture | No implementado/no ejecutado |
| Varias filas | Fixture con múltiples rutas | Todas las filas válidas conservan su orden de origen, salvo que se apruebe otro orden | Unit test de dominio | Orden contractual pendiente; no implementado/no ejecutado |
| Fila `On-link` | Fila con `On-link` en lugar de gateway IPv4 | Fila omitida | Unit test de dominio | No implementado/no ejecutado |
| Encabezados localizados | Salida con encabezados en español e inglés, datos numéricos idénticos | El parseo no depende de las etiquetas del encabezado | Unit test con fixtures | No implementado/no ejecutado |
| Fila incompleta | Menos de cuatro IPv4 o métrica no entera | No se emite una ruta parcial o fabricada | Unit test de dominio | No implementado/no ejecutado |
| GET sin parámetros | Solicitud a la ruta aprobada | Respuesta 200 conforme al esquema cuando el parseo tiene éxito | Test API | No implementado/no ejecutado |
| Timeout/proceso fallido | Runner falso con timeout o exit code de error | Resultado según política HTTP aún pendiente | Test API | Contrato pendiente; no implementado/no ejecutado |
| Límite de concurrencia | Más de cinco solicitudes simultáneas | No más de cinco consultas activas; efecto de la sexta según decisión pendiente | Test API concurrente | Saturación pendiente; no implementado/no ejecutado |

Usar fixtures deterministas basadas en salidas representativas de `route print -4`; no depender de la tabla real del equipo ni de conectividad externa. Comparar el parser de Route Table con las expectativas del parser de Route Analyzer para evitar divergencias.

## Ejecución y última verificación

- **Comando:** ninguno; tarea documental.
- **Entorno:** no aplica.
- **Fecha:** 2026-10-20.
- **Resultado observado:** pruebas no ejecutadas; no hay pruebas específicas de Route Table verificadas en esta tarea.
- **Pendientes:** crear los tests al implementar y definir el contrato de errores y salida vacía antes de cerrar la integración HTTP.
