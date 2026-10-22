# Requisitos — Asistente de resolución de problemas

> Estado: alcance aprobado para la herramienta 22. El catálogo fundacional la marca pendiente de desarrollo e integración; este documento no afirma que esté implementada.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 5, herramienta 22.
- **Propósito:** guiar al técnico en el diagnóstico de problemas comunes de red mediante síntomas, causas posibles y pasos de solución.
- **Incluye:** consulta de un árbol de decisión estático mediante un identificador de síntoma y devolución de sus causas y pasos.
- **No incluye:** consultas a la red, ejecución de comprobaciones, acceso al sistema operativo ni persistencia de resultados.
- **Familias/protocolos admitidos:** los síntomas describen problemas generales de conectividad; no realizan cálculos ni operaciones de protocolo.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| TRB-F-001 | Mantener un catálogo estático de síntomas | El dominio contiene `SYMPTOM_DATABASE` | Se dispone de al menos `sin_internet`, `internet_lento` y `dns_falla`, con sus nombres descriptivos | Aprobado |
| TRB-F-002 | Asociar causas a cada síntoma | Cada síntoma del catálogo | Cada síntoma tiene al menos tres causas posibles; cada causa tiene un título y una lista de pasos de solución en texto | Aprobado |
| TRB-F-003 | Consultar por identificador | `symptom_id` en `GET /api/v1/tools/troubleshooter/symptoms/{symptom_id}` | Para un identificador conocido, la API devuelve `symptom_id`, `symptom_name` y `causes` | Aprobado |
| TRB-F-004 | Mantener los pasos en orden | Consulta de síntoma conocido | Cada causa devuelve sus pasos como strings en el orden definido en el catálogo | Aprobado |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| TRB-NF-001 | Arquitectura | El dominio contiene datos estáticos y lógica de consulta pura; no necesita runner | El dominio no depende de API, base de datos, red ni sistema operativo | Aprobado |
| TRB-NF-002 | Concurrencia | La capa API usa `asyncio.Semaphore(5)` | Las solicitudes pasan por el semáforo de cinco permisos | Aprobado; política al agotarse pendiente |
| TRB-NF-003 | Seguridad | Los textos del catálogo se presentan como texto, no como HTML ejecutable | La interfaz no interpreta los datos devueltos como HTML | Aprobado como directriz de presentación |

## Criterios de aceptación

- El catálogo incluye los identificadores `sin_internet`, `internet_lento` y `dns_falla` con los nombres descriptivos aprobados.
- Cada síntoma tiene al menos tres causas; cada causa incluye un título y al menos una lista de pasos representada como strings.
- Consultar un identificador existente devuelve HTTP 200 y el esquema documentado.
- Los pasos y las causas conservan el orden almacenado en el catálogo.
- La herramienta no consulta red, no ejecuta comandos y no persiste datos.
- El comportamiento HTTP para un `symptom_id` desconocido y para el agotamiento del semáforo queda pendiente de definición antes de implementar el contrato completo.

## Fuentes y pendientes

- **Decisiones aplicables:** [TRB-DEC-01](decision-log.md).
- **Fuente de alcance:** [catálogo fundacional, herramienta 22](../../fundacional/catalogo.md).
- **Pendiente de aprobación o investigación:** contenido específico y pasos de cada causa; comportamiento y error HTTP para identificador desconocido; política de saturación del semáforo.
