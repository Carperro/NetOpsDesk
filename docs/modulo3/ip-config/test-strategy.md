# Estrategia de pruebas — Asistente de configuración IP

> Cobertura prevista para una implementación futura. No hay pruebas de esta herramienta implementadas ni ejecutadas como parte de esta tarea documental.

## Alcance y capas

| Capa | Archivo(s) | Qué verifica | Estado |
|---|---|---|---|
| Dominio | Archivo por determinar; se espera `tests/test_ip_config_domain.py` | Acciones admitidas, requisitos condicionales, validación y generación determinista de texto | Pendiente |
| API | Archivo por determinar; se espera `tests/test_api_ip_config.py` | Método/ruta, modelo de request, respuesta y errores conforme al contrato aprobado | Pendiente |
| Interfaz/integración | Pruebas estáticas o de interfaz por determinar | Formulario por acción, presentación segura del comando y copia al portapapeles sin ejecución | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| IPC-F-001 | `renew_dhcp` con interfaz válida | Comando de renovación y explicación en español | Unit test de dominio | No implementado/no ejecutado |
| IPC-F-002 | `set_dhcp` con interfaz válida | Comando para DHCP y explicación en español | Unit test de dominio | No implementado/no ejecutado |
| IPC-F-003 | `set_static` con IP, máscara y gateway válidos | Comando estático y explicación | Unit test de dominio | No implementado/no ejecutado |
| Entradas inválidas | Acción desconocida, campos ausentes, IPv4 inválida o máscara no válida | Error tipado, sin texto de comando | Unit test de dominio | Reglas por cerrar; no implementado/no ejecutado |
| Inyección en valores | Nombre de interfaz con comillas, saltos de línea o metacaracteres | Rechazo o codificación segura según gramática aprobada; no se agregan argumentos | Unit/API test | Gramática pendiente; no implementado/no ejecutado |
| No ejecución | Solicitud válida | Generación sin invocar procesos ni cambiar configuración | Test unitario/estático | No implementado/no ejecutado |
| Respuesta HTTP | Request válido e inválido | Coincide con contrato y errores aprobados | Test de contrato API | Contrato parcial; no implementado/no ejecutado |
| Copiar desde interfaz | Comando generado | Se copia exactamente como texto; ningún evento lo ejecuta | Test frontend | No implementado/no ejecutado |

Los comandos esperados deben fijarse solo después de verificar la sintaxis de Windows elegida y aprobar el contrato. No se realizarán pruebas que ejecuten comandos de configuración sobre una interfaz real.

## Ejecución y última verificación

- **Comando:** ninguno; tarea documental.
- **Entorno:** no aplica.
- **Fecha:** 2026-10-20.
- **Resultado observado:** pruebas no ejecutadas; no hay implementación de la herramienta verificada en este trabajo.
- **Pendientes:** convertir los casos previstos en pruebas al autorizar implementación y cerrar primero los detalles contractuales anotados en `api-contracts.md` y `decision-log.md`.
