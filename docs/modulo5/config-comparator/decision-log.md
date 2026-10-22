# Registro de decisiones — Comparador de configuraciones

Este registro contiene decisiones específicas de la herramienta 23 aprobadas por el usuario. La existencia de este documento no implica que la herramienta esté implementada.

## Decisiones

### CFG-DEC-01 — Comparación textual con difflib

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Se necesita identificar diferencias entre dos bloques de texto de configuración sin acceder a dispositivos ni archivos.
- **Decisión:** El dominio `netops_desk/config_comparator.py` realiza una comparación pura usando `difflib.unified_diff`. Recibe `config_a` (original) y `config_b` (nuevo), y devuelve `diff_lines` como array de strings y `has_changes` como booleano. Al menos uno de los textos debe tener contenido. La capa API usa `asyncio.Semaphore(5)`.
- **Motivo:** La biblioteca estándar proporciona el formato de diff unificado requerido sin añadir dependencias ni efectos externos.
- **Alternativas:** No registradas.
- **Consecuencias:** El dominio no necesita base de datos, sistema operativo, red ni runner. Los parámetros de formato, errores y límite de longitud se precisan en CFG-DEC-02 y CFG-DEC-03.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 23.

### CFG-DEC-02 — Errores y límite de longitud

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Evitar comparar solicitudes vacías o textos excesivamente grandes y definir la respuesta ante saturación.
- **Decisión:** Si ambos textos están vacíos, el dominio lanza `DomainError` con código `empty_configs`, traducido por el handler global a HTTP 422. Si se agota `asyncio.Semaphore(5)`, la API responde HTTP 429 con `too_many_requests`. El modelo Pydantic limita `config_a` y `config_b` a 50.000 caracteres cada uno.
- **Motivo:** Mantener la validación de la regla de negocio en dominio, limitar el tamaño de entrada en la frontera API y rechazar solicitudes sin capacidad concurrente.
- **Alternativas:** No registradas.
- **Consecuencias:** El contrato y las pruebas deben cubrir ambos errores y el límite de longitud; el código específico del error Pydantic por longitud sigue el manejo común de validación del Módulo 5.

### CFG-DEC-03 — Parámetros del diff unificado

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** El resultado se entrega como array de strings y debe evitar terminadores duplicados.
- **Decisión:** Invocar `difflib.unified_diff` con `fromfile="Config A"`, `tofile="Config B"` y `lineterm=""`.
- **Motivo:** Identificar claramente ambos lados del diff y mantener los elementos del array sin saltos de línea agregados por el generador.
- **Alternativas:** No registradas.
- **Consecuencias:** Los tests del contrato deben verificar cabeceras `Config A`/`Config B` y que cada elemento no incluya el terminador añadido por `lineterm`.

## Pendientes de decisión

- Definir si strings formados solo por espacios cuentan como contenido.
- Definir si strings formados solo por espacios cuentan como contenido.
- Definir el alcance del semáforo entre procesos workers.
- Definir si se requieren límites de transporte adicionales al máximo de caracteres por campo.
