# Registro de decisiones — Generador de comandos

Este registro contiene decisiones específicas de la herramienta 24. Las decisiones globales se consultan en [`docs/fundacional/decision-log.md`](../../fundacional/decision-log.md). La existencia de este documento no implica que la herramienta esté implementada.

## Decisiones

### CMD-DEC-01 — Generación de texto sin ejecución

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** La herramienta prepara comandos de red y ayuda a comprender sus parámetros.
- **Decisión:** La herramienta genera un string de comando y una explicación del propósito y de cada parámetro. No ejecuta comandos ni invoca `subprocess`. La interfaz presenta el string como texto copiable en un `<textarea>` o `<code>`.
- **Motivo:** La solicitud limita la función a preparar y explicar el comando.
- **Alternativas:** Ejecutar el comando desde la aplicación; fuera del alcance explícito.
- **Consecuencias:** El usuario copia el texto y decide dónde usarlo. La respuesta incluye `requires_admin` como booleano.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 24.

### CMD-DEC-02 — Plantillas estáticas y dominio puro

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** La plantilla seleccionada determina los campos y el comando resultante.
- **Decisión:** El dominio objetivo `netops_desk/command_generator.py` usa diccionarios estáticos y lógica condicional para armar el comando. Los tipos admitidos son `ping`, `tracert`, `ipconfig`, `netstat` y `nslookup`.
- **Motivo:** Mantener la generación desacoplada de la API y sin efectos del sistema operativo.
- **Alternativas:** No registradas.
- **Consecuencias:** La API adapta entradas y salidas del dominio; no se requieren procesos externos para generar la respuesta.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 24.

### CMD-DEC-03 — Whitelist y privilegios por comando

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Limitar comandos y opciones a un catálogo explícito y determinar si el uso requiere consola de administrador.
- **Decisión:** `ping` requiere objetivo y permite `-t`, `-a` (sin administrador); `tracert` requiere objetivo y permite `-d` (sin administrador); `nslookup` requiere objetivo y no permite opciones (sin administrador); `ipconfig` acepta objetivo vacío u omitido, permite `/all`, `/flushdns`, `/release`, `/renew` y requiere administrador solo para las últimas tres; `netstat` acepta objetivo vacío u omitido, permite `-a`, `-n`, `-b` y requiere administrador solo para `-b`. Se rechaza cualquier tipo u opción fuera de esta whitelist.
- **Motivo:** Producir comandos limitados a plantillas conocidas y comunicar cuándo se requieren privilegios.
- **Alternativas:** No registradas.
- **Consecuencias:** La API devuelve `invalid_command_type`, `missing_target`, `invalid_target` o `invalid_option` ante los casos definidos; la respuesta `requires_admin` sigue esta matriz.
- **Aprobación:** Resolución explícita del usuario al solicitar el cierre de documentación el 2026-10-20.

### CMD-DEC-04 — Errores HTTP y semáforo

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Establecer respuestas para entradas inválidas y solicitudes concurrentes.
- **Decisión:** `invalid_command_type`, `missing_target`, `invalid_target` e `invalid_option` responden HTTP 422. La API usa `asyncio.Semaphore(5)` y, al agotarse, responde HTTP 429 con `too_many_requests`.
- **Motivo:** Proporcionar errores estables para validación y limitar solicitudes concurrentes.
- **Alternativas:** No registradas.
- **Consecuencias:** Contrato y pruebas deben comprobar cada código y estado. El sobre común HTTP debe seguir la política aplicable al Módulo 5.
- **Aprobación:** Resolución explícita del usuario al solicitar el cierre de documentación el 2026-10-20.

## Pendientes de decisión

- La gramática exacta del dominio/IP válido y el sobre transversal de errores HTTP aplicable al Módulo 5 se deben concretar antes de implementar/verificar la API.
- La sintaxis específica del comando generado para cada plantilla debe verificarse al implementar.