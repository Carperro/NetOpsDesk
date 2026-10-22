# Estrategia de pruebas — Analizador de direcciones MAC

> Cobertura prevista para una herramienta pendiente de implementación. No hay aquí afirmaciones de pruebas implementadas o ejecutadas.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_mac_analyzer_domain.py` | Validación, normalización, preservación del original y traducción de resultado del runner | Pendiente |
| Runner | Por definir | Adaptación de `mac-vendor-lookup` y respuesta cuando no se encuentra fabricante | Pendiente |
| API | `tests/test_api_mac_analyzer.py` | Request/response, códigos de error y contrato HTTP | Pendiente |
| Interfaz/integración | Archivo de pruebas frontend por definir | Presentación segura de valores devueltos y mensajes de error | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| MAC-F-001: forma con dos puntos | `00:1A:2B:3C:4D:5E` | Aceptada; seis octetos válidos | Dominio/API | Pendiente; no ejecutado |
| MAC-F-001: forma con guiones | `00-1a-2b-3c-4d-5e` | Aceptada | Dominio/API | Pendiente; no ejecutado |
| MAC-F-002: normalización | `00-1A-2B-3C-4D-5E` | `00:1a:2b:3c:4d:5e`; original conservado | Dominio | Pendiente; no ejecutado |
| Entrada inválida | Cantidad incorrecta de octetos, dígitos no hexadecimales o separadores no admitidos | Rechazo de validación; no se consulta el runner | Dominio/API | Pendiente; no ejecutado |
| Fabricante encontrado | Runner falso devuelve un fabricante | `vendor` contiene ese valor | Dominio/API | Pendiente; no ejecutado |
| Sin coincidencia OUI | Runner falso indica ausencia | HTTP 200 y `vendor: "Desconocido"` | Dominio/API | Pendiente; no ejecutado |
| Independencia de red | Runner falso; sin servicio externo | El dominio obtiene resultado exclusivamente del runner | Dominio | Pendiente; no ejecutado |
| Concurrencia | Más de cinco solicitudes simultáneas | Verificar límite y política una vez que se decida espera o rechazo | API | Pendiente; política no definida |

Los resultados de normalización se pueden comprobar con reglas explícitas de seis octetos hexadecimales y formatos de separador aprobados. Las pruebas del fabricante deben usar dobles del runner; no deben depender de una consulta de red ni de que una entrada particular exista en una versión cambiante de la base OUI.

## Ejecución y última verificación

- **Comando:** No ejecutado; la tarea actual crea documentación y no implementa pruebas.
- **Entorno:** No aplica a esta revisión documental.
- **Fecha:** 2026-10-20.
- **Resultado observado:** No se ejecutaron pruebas.
- **Pendientes:** implementar la herramienta y las pruebas; definir contrato común de errores, saturación del semáforo y mantenimiento de datos OUI.
