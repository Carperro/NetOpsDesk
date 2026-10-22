# Estrategia de pruebas — Generador de informes de diagnóstico

> Cobertura prevista para una herramienta pendiente de implementación. No se afirma que existan o se hayan ejecutado pruebas.

## Alcance y capas

| Capa | Archivo(s) objetivo | Qué verifica | Estado |
|---|---|---|---|
| Dominio | `tests/test_report_generator_domain.py` | Validación de estructura, fecha por defecto y generación determinista de Markdown | Pendiente |
| API | `tests/test_api_report_generator.py` | Ruta, request/response, validación y concurrencia | Pendiente |
| Interfaz/integración | Pruebas frontend por definir | Presentación como texto y copia del reporte | Pendiente |

## Matriz de casos

| Requisito/caso | Entrada | Resultado esperado | Prueba que lo verifica | Estado de ejecución |
|---|---|---|---|---|
| Reporte básico | Título, autor y un hallazgo | String Markdown con los datos suministrados | Dominio/API | Pendiente; no ejecutado |
| Varios hallazgos | Dos o más pares `step`/`result` | Se conservan todos y su orden de entrada | Dominio | Pendiente; no ejecutado |
| Fecha explícita | Campo `date` suministrado | Se refleja la fecha, sujeto al formato aprobado | Dominio/API | Pendiente; formato sin cerrar |
| Fecha omitida | Request sin `date` | Se usa la fecha actual según la política temporal aprobada | Dominio/API | Pendiente; zona horaria sin cerrar |
| Conclusión opcional | Request con y sin `conclusion` | Se incorpora solo cuando se suministra | Dominio | Pendiente; no ejecutado |
| Título vacío | `title` vacío | Rechazo de validación | Dominio/API | Pendiente; código HTTP por definir |
| Hallazgos vacíos | `findings: []` | Rechazo de validación | Dominio/API | Pendiente; código HTTP por definir |
| Salida de texto | Datos con caracteres Markdown/HTML | La API devuelve un string; la interfaz lo presenta sin interpretarlo como HTML | API/frontend | Pendiente; escaping Markdown por definir |
| Sin efectos externos | Ejecutar generación del dominio | No se usa red, base de datos, OS ni conversión a PDF/imagen | Dominio | Pendiente; no ejecutado |
| Semáforo agotado | Más de cinco solicitudes concurrentes | Resultado conforme a política de saturación a definir | API | Pendiente; política no definida |

Las aserciones de composición deben comparar texto esperado conocido, sin depender de ordenamientos externos. Para las pruebas de fecha por defecto se debe controlar el reloj o inyectar la fecha para evitar resultados dependientes del día de ejecución; la técnica exacta se definirá al implementar.

## Ejecución y última verificación

- **Comando:** No ejecutado; esta tarea solo crea documentación.
- **Entorno:** No aplica a la auditoría documental.
- **Fecha:** 2026-10-20.
- **Resultado observado:** No se ejecutaron pruebas.
- **Pendientes:** implementar dominio/API/interfaz y cerrar formato Markdown, política temporal, validaciones secundarias, errores y saturación.
