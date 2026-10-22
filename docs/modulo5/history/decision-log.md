# Registro de decisiones — Historial de diagnósticos

Este registro contiene las decisiones específicas de la herramienta 25. Las decisiones globales se consultan en [`docs/fundacional/decision-log.md`](../../fundacional/decision-log.md); DEC-018 se documenta localmente en el registro de Inventario y se reutiliza en IPAM.

## Decisiones

### DEC-HISTORY-01 — Tabla de historial en la base compartida

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha de registro:** 2026-10-20.
- **Contexto:** La Herramienta 25 necesita conservar y consultar entradas y compartir el archivo de base de datos utilizado por Inventario e IPAM.
- **Decisión:** Persistir registros en la tabla `history` del archivo SQLite compartido `netops.db`, conforme a DEC-018. La tabla incluye `id`, `tool_name`, `action`, `result_status`, `details` y `created_at`.
- **Motivo:** Reutilizar la persistencia local aprobada y conservar el historial entre ejecuciones.
- **Alternativas:** No registradas.
- **Consecuencias:** Usar SQLite nativo (`sqlite3`), sin ORM, a través de un repositorio dedicado; las reglas adicionales de esquema se especifican en DEC-HISTORY-03.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 25; reutilización de DEC-018 indicada explícitamente.

### DEC-HISTORY-02 — Gestión independiente del historial

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha de registro:** 2026-10-20.
- **Contexto:** El guardado automático desde cada herramienta acoplaría sus dominios con la base y el ciclo de vida del historial.
- **Decisión:** History se gestiona de forma independiente. Las herramientas 1–24 no se modifican para guardar registros automáticamente. La interfaz de History permite crear entradas manualmente; las herramientas podrán llamar al endpoint en el futuro.
- **Motivo:** Preservar el aislamiento de los dominios existentes y permitir una integración opcional posterior.
- **Alternativas:** Acoplar los dominios 1–24 al repositorio de historial; descartada para el alcance actual.
- **Consecuencias:** La creación manual es el flujo inicial; una integración futura se realizará mediante la API.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 25.

### DEC-HISTORY-03 — Tipos, fecha de creación y orden del listado

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha de registro:** 2026-10-20.
- **Contexto:** Fijar el esquema SQLite y el orden cronológico reproducible de las consultas.
- **Decisión:** `id` usa `INTEGER PRIMARY KEY AUTOINCREMENT`. `tool_name`, `action`, `result_status`, `details` y `created_at` usan `TEXT`. `created_at` se genera con `datetime.now().isoformat()`. El listado usa `ORDER BY created_at DESC, id DESC`.
- **Motivo:** Guardar fechas ISO como texto y definir un desempate estable para timestamps iguales mediante el ID descendente.
- **Alternativas:** No registradas.
- **Consecuencias:** El repositorio genera la fecha al crear y ordena por fecha e ID. `details` tiene default de aplicación `""`; la obligatoriedad de `result_status` no fue especificada explícitamente.
- **Aprobación:** Resolución explícita del usuario al solicitar el cierre de documentación el 2026-10-20.

### DEC-HISTORY-04 — Validaciones de campos, error y concurrencia

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha de registro:** 2026-10-20.
- **Contexto:** Definir los campos requeridos y las respuestas para eliminación y límite concurrente.
- **Decisión:** `tool_name` y `action` son obligatorios. `details` es opcional y toma `""` por defecto. Eliminar un ID inexistente devuelve HTTP 422 `not_found`. La API usa `asyncio.Semaphore(5)` y responde HTTP 429 `too_many_requests` cuando se agota.
- **Motivo:** Definir validaciones y límites operativos de la herramienta.
- **Alternativas:** No registradas.
- **Consecuencias:** Pruebas de contrato cubren los estados `200`, `201`, `204`, `422` y `429`. La obligatoriedad de `result_status` no quedó expresamente resuelta.
- **Aprobación:** Resolución explícita del usuario al solicitar el cierre de documentación el 2026-10-20.

## Pendientes de decisión

- Confirmar si `result_status` es obligatorio en el request; las reglas explícitas solo califican `tool_name`, `action` y `details`.
- Precisar el sobre/códigos del resto de errores de esquema con el contrato común aplicable al Módulo 5.