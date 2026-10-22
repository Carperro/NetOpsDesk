# Estrategia de pruebas — Visor de caché ARP

> Cobertura prevista para una implementación futura. No hay pruebas ARP observadas en `tests/` y no se ejecutaron pruebas en esta tarea.

## Alcance y capas

| Capa | Archivo(s) | Qué verifica | Estado |
|---|---|---|---|
| Dominio | Por determinar; se espera `tests/test_arp_viewer_domain.py` | Decodificación, secciones de interfaz, filas ARP, normalización y filas inválidas | Pendiente |
| Adaptador/API | Por determinar; se espera `tests/test_api_arp_viewer.py` | Comando fijo, `shell=False`, timeout, método GET, respuesta y errores | Pendiente |
| Interfaz/integración | Prueba estática/frontend por determinar | Renderizado de entradas y estados vacíos/errores como texto | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Entrada dinámica en español | Bytes con sección `Interfaz: ...` y fila con `dinámico` | Interfaz, IP, MAC y tipo `dynamic` correctos | Unit test con runner falso | No implementado/no ejecutado |
| Entrada dinámica en inglés | Bytes con encabezado y marcador `dynamic` | Misma estructura normalizada | Unit test con runner falso | No implementado/no ejecutado |
| Entrada estática | Fila válida con marcador estático reconocido | `entry_type: static` | Unit test con runner falso | Idioma por definir; no implementado/no ejecutado |
| Varias interfaces | Dos encabezados y filas asociadas | Cada entrada conserva su `interface_ip` | Unit test de dominio | No implementado/no ejecutado |
| MAC con mayúsculas | Dirección válida en mayúsculas | MAC normalizada a minúsculas con guiones | Unit test de dominio | No implementado/no ejecutado |
| Fila incompleta/malformada | IP sin MAC o tipo no reconocido | Fila ignorada; no se inventa una asociación | Unit test de dominio | No implementado/no ejecutado |
| Bytes con codificación inválida | Salida que contiene bytes no decodificables | Decodificación tolerante mediante reemplazo | Unit test de dominio | No implementado/no ejecutado |
| Caché vacía | Salida sin filas de entrada | `entries: []` o error si no se reconoce la estructura; decisión por cerrar | Unit/API test | No implementado/no ejecutado |
| Comando y seguridad | Solicitud GET | Runner recibe exactamente `arp -a`, con shell deshabilitado | Test del adaptador | No implementado/no ejecutado |
| Timeout y fallo del comando | Runner simulado con timeout/error | Estado y código conforme a contrato pendiente | Test API | Contrato pendiente; no implementado/no ejecutado |
| Límite de concurrencia | Seis o más solicitudes simultáneas | Máximo de cinco operaciones activas según política acordada | Test API concurrente | Semántica de saturación pendiente; no implementado/no ejecutado |

Las fixtures deben ser salidas capturadas o construidas de forma controlada, sin depender de la tabla ARP real de la máquina ni de conectividad externa. Ampliar idiomas requiere muestras representativas y pruebas específicas.

## Ejecución y última verificación

- **Comando:** ninguno; tarea de documentación.
- **Entorno:** no aplica.
- **Fecha:** 2026-10-20.
- **Resultado observado:** pruebas no ejecutadas; la inspección estática no encontró archivos ARP en `src/` ni en `tests/`.
- **Pendientes:** crear pruebas junto con la implementación y decidir primero los contratos de error, saturación, límites de salida y compatibilidad de idioma.
