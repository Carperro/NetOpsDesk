# Registro de decisiones — Asistente de resolución de problemas

Este registro contiene decisiones específicas de la herramienta 22 aprobadas por el usuario. La existencia de este documento no implica que la herramienta esté implementada.

## Decisiones

### TRB-DEC-01 — Árbol de decisión estático en el dominio

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Se requiere orientar el diagnóstico con causas y pasos sin realizar comprobaciones automáticamente.
- **Decisión:** El dominio `netops_desk/troubleshooter.py` contiene el diccionario estático `SYMPTOM_DATABASE`, sin necesidad de inyección de dependencias. Se consultará mediante `GET /api/v1/tools/troubleshooter/symptoms/{symptom_id}`. El catálogo mínimo contiene `sin_internet`, `internet_lento` y `dns_falla`; cada síntoma tendrá al menos tres causas, y cada causa un título y pasos de solución como strings. La API usa `asyncio.Semaphore(5)`.
- **Motivo:** Mantener la herramienta como guía estática, sin depender de base de datos, red ni sistema operativo.
- **Alternativas:** No registradas.
- **Consecuencias:** La consulta no produce mediciones ni modifica el sistema; el contenido del catálogo se mantiene en el dominio.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 22.

### TRB-DEC-02 — Error de síntoma desconocido y saturación

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Definir la respuesta para identificadores fuera del catálogo y para solicitudes cuando se ocupan los permisos concurrentes.
- **Decisión:** Si `symptom_id` no existe, el dominio lanza `DomainError` con código `invalid_symptom`, que el handler global mapea a HTTP 422. La API usa `asyncio.Semaphore(5)` y, si se agota, responde HTTP 429 con código `too_many_requests`.
- **Motivo:** Mantener la validación del catálogo en el dominio y distinguirla de la saturación del servicio.
- **Alternativas:** No registradas.
- **Consecuencias:** El contrato API y las pruebas deben cubrir ambos códigos y estados. El alcance entre varios procesos workers no queda definido por esta decisión.
- **Aprobación:** Instrucción explícita del usuario al cerrar la documentación de la herramienta 22.

## Pendientes de decisión

- Definir las causas y los pasos concretos para cada síntoma.
- Definir la política de coordinación del semáforo entre procesos workers, si el despliegue deja de usar un único proceso.
