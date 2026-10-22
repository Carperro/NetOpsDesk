# Estrategia de pruebas — Analizador de gateway y rutas

## Estado

Plan de pruebas para la futura implementación. El catálogo marca la herramienta pendiente; los casos de esta estrategia no se consideran implementados ni ejecutados. La cifra de tests indicada en la solicitud es contexto del usuario y no fue verificada en esta tarea.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Dominio/parser | A definir durante implementación | Decodificación, identificación de gateway, parsing y normalización de rutas | Pendiente |
| Runner | A definir durante implementación | Comandos fijos, argumentos, `shell=False`, bytes y timeouts | Pendiente |
| API | A definir durante implementación | GET sin body, respuesta, errores y semáforo | Pendiente |
| Interfaz/integración | A definir con integración frontend | Presentación de gateway/rutas y mensajes de error | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| GET sin body | Petición a endpoint sin parámetros/body | Respuesta según contrato, sin solicitar datos de entrada | Test HTTP de contrato | Pendiente/no ejecutado |
| Gateway español | Fixture de `ipconfig` con `Puerta de enlace predeterminada` | Dirección IPv4 extraída | Test unitario de parser | Pendiente/no ejecutado |
| Gateway inglés | Fixture de `ipconfig` con `Default Gateway` | Mismo resultado normalizado que fixture español | Test unitario de parser | Pendiente/no ejecutado |
| Varias interfaces | Fixture con varias secciones e interfaces | No mezclar gateway e interfaz entre secciones; desempate según regla aprobada | Test unitario de parser | Pendiente/no ejecutado |
| Rutas IPv4 | Fixture estructural de `route print -4` | Destino, máscara, gateway, interfaz y métrica completos | Test unitario de parser | Pendiente/no ejecutado |
| Cabeceras localizadas | Fixtures español e inglés con cabeceras distintas | Las cabeceras se ignoran y las filas se identifican por su estructura | Test unitario de parser | Pendiente/no ejecutado |
| Ruta on-link | Fixture de ruta sin gateway IPv4 convencional | Representación según decisión específica | Test unitario de parser | Pendiente; formato por definir |
| Métrica/filas malformadas | Tokens incompletos o no numéricos | No producir rutas parciales ficticias; registrar error controlado | Test unitario de parser | Pendiente |
| Comandos exactos | Runner invocado por el dominio | Ejecuta `ipconfig` y `route print -4`, sin shell y sin datos variables | Test unitario del runner con mock | Pendiente/no ejecutado |
| Timeout de cada comando | Mock excede 10 segundos | El proceso se limita/cancela según contrato | Test del runner | Pendiente; status HTTP por definir |
| Fallo de un comando | Ejecutable ausente, error de permiso o exit code distinto | No ocultar el fallo ni devolver éxito inventado | Test runner/API | Pendiente; política de parcialidad por definir |
| Concurrencia | Cinco solicitudes simultáneas y una adicional | Límite global de cinco con un worker; conducta del exceso según decisión | Test API/concurrencia | Pendiente; espera/429 sin decisión |
| Seguridad | Request sin parámetros y mock de proceso | Ningún input externo se añade a los argumentos; `shell=False` | Test del runner | Pendiente/no ejecutado |

## Datos esperados independientes

Usar fixtures capturados o redactados de salidas de Windows en español e inglés y revisar manualmente las direcciones, máscaras y métricas. Los datos de prueba no deben depender de la configuración cambiante del equipo del desarrollador ni ejecutarse en hosts públicos. La selección del gateway esperado debe calcularse conforme a la regla que se apruebe para métricas/rutas múltiples.

## Ejecución y última verificación

- **Comando:** No ejecutado en esta tarea.
- **Entorno:** Windows/Python del proyecto según contexto; sin verificación dinámica aquí.
- **Fecha:** 2026-10-20 (creación de esta estrategia, no fecha de ejecución de pruebas).
- **Resultado observado:** Sin resultados de pruebas para esta herramienta.
- **Pendientes:** implementar los casos, definir decisiones abiertas y ejecutar la suite con el intérprete configurado del proyecto.
