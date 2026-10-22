# Requisitos — Comparador de configuraciones

> Estado: alcance aprobado para la herramienta 23. El catálogo fundacional la marca pendiente de desarrollo e integración; este documento no afirma que esté implementada.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 5, herramienta 23.
- **Propósito:** identificar y presentar diferencias entre dos bloques de texto de configuración.
- **Incluye:** recibir `config_a` y `config_b`, compararlos y devolver las líneas de un diff unificado junto con un indicador de cambios.
- **No incluye:** conexión a dispositivos, lectura o escritura de archivos, ejecución de comandos, persistencia ni generación de informes binarios.
- **Familias/protocolos admitidos:** cualquier texto proporcionado por el cliente; el dominio no interpreta semántica específica de un fabricante o protocolo.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| CFG-F-001 | Recibir dos configuraciones | Strings `config_a` y `config_b` | El dominio recibe ambos textos para compararlos | Aprobado |
| CFG-F-002 | Exigir contenido en al menos una entrada | No se permite que ambos textos estén vacíos | La solicitud con ambos textos vacíos se rechaza | Aprobado |
| CFG-F-003 | Generar diff unificado | Al menos uno de los textos contiene contenido | `diff_lines` es un array de strings con el resultado de `difflib.unified_diff` | Aprobado |
| CFG-F-004 | Informar si hay diferencias | Comparación de `config_a` y `config_b` | `has_changes` es booleano y refleja si el contenido difiere | Aprobado |
| CFG-F-005 | Representar configuraciones idénticas | Ambos textos contienen el mismo contenido | `has_changes` es `false` y `diff_lines` no contiene diferencias | Aprobado |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| CFG-NF-001 | Arquitectura | La comparación es lógica pura basada en la biblioteca estándar `difflib` | El dominio no depende de FastAPI, base de datos, sistema operativo ni red | Aprobado |
| CFG-NF-002 | Concurrencia | La capa API usa `asyncio.Semaphore(5)` | Las solicitudes pasan por el semáforo de cinco permisos | Aprobado; política al agotarse pendiente |
| CFG-NF-003 | Seguridad | Los textos de configuración se tratan como datos no confiables | La interfaz presenta el resultado como texto y no lo interpreta como HTML | Directriz aprobada |

## Criterios de aceptación

- Dos configuraciones distintas producen un diff unificado y `has_changes: true`.
- Dos configuraciones idénticas producen un diff vacío y `has_changes: false`.
- Si una configuración está vacía y la otra no, la solicitud es válida y se representa la diferencia.
- Si ambas configuraciones están vacías, la solicitud se rechaza.
- El dominio usa `difflib.unified_diff` y no accede a archivos, dispositivos, red ni sistema operativo.
- Los valores recibidos se muestran como texto, nunca como HTML ejecutable.

## Fuentes y pendientes

- **Decisiones aplicables:** [CFG-DEC-01](decision-log.md).
- **Fuente de alcance:** [catálogo fundacional, herramienta 23](../../fundacional/catalogo.md).
- **Pendiente de aprobación o investigación:** tratamiento de strings compuestos solo por espacios; orden A/B y parámetros exactos del formato unificado; códigos/status HTTP de validación y saturación; límite de tamaño de entrada.
