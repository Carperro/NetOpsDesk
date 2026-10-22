# Registro de decisiones — Estado de adaptadores

Este registro contiene decisiones específicas de la herramienta 15 y decisiones aplicables al Módulo 3 expresamente aprobadas para esta tarea. La existencia del documento no implica implementación.

## Decisiones aprobadas

### DEC-017 — Aprobación de `psutil` para información de interfaces

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Alcance:** Herramienta 11 y próximas herramientas del Módulo 3 que necesiten información nativa de interfaces de red, sujeto a justificar su uso concreto.
- **Contexto:** Leer `ipconfig /all` mediante `subprocess` requiere parsear salida textual dependiente del idioma y formato de Windows.
- **Decisión:** Aprobar `psutil` para obtener direcciones, máscara, MAC, estado y velocidad de interfaces mediante `psutil.net_if_addrs()` y `psutil.net_if_stats()` en el runner de infraestructura.
- **Motivo:** Evitar el parseo frágil de `ipconfig` y obtener datos estructurados de interfaces.
- **Alternativas:** Parsear `ipconfig /all` para todos los campos; descartado porque su salida depende de idioma y formato para datos que psutil entrega estructurados.
- **Consecuencias:** `psutil` debe declararse y fijarse en el lockfile al autorizar la preparación/implementación; este pase documental no instala ni añade la dependencia. El dominio no debe depender directamente de psutil.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 11, 2026-10-20.

### ADP-DEC-001 — Consulta de solo lectura sin parámetros

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** Exponer información local mediante una operación GET sin parámetros de entrada.
- **Consecuencia:** Los datos corresponden al servidor de NetOps Desk; la operación no modifica adaptadores.

### ADP-DEC-002 — Runner inyectado

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** El dominio `netops_desk/adapters.py` recibe un `AdaptersRunner`. El runner usa `psutil.net_if_stats()` para estado, velocidad, MTU y soporte de multicast y construye objetos estructurados; el dominio valida y devuelve el resultado.

### ADP-DEC-003 — Contrato inicial de campos

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** La respuesta incluye por adaptador `name`, `is_up`, `speed_mbps`, `mtu` e `is_multicast`.

### ADP-DEC-004 — Límite de concurrencia

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** La capa API usará `asyncio.Semaphore(5)` global con un único worker de Uvicorn.
- **Consecuencias:** No ejecutar varios workers en este despliegue, ya que cada proceso tendría un semáforo independiente. La conducta ante saturación sigue pendiente.

### ADP-DEC-005 — Campos de estado, velocidad y MTU desde `psutil.net_if_stats()`

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** El runner obtiene `is_up`, `speed_mbps`, `mtu` e `is_multicast` únicamente de `psutil.net_if_stats()`. No se usa `subprocess` ni `ipconfig` para esta herramienta.
- **Motivo:** La herramienta 15 no lee IPs ni DNS; la fuente estructurada de `psutil` cubre todos los campos del contrato sin parseo de texto del sistema operativo.
- **Consecuencias:** La herramienta hereda la dependencia `psutil` aprobada en DEC-017. El campo `is_multicast` dependerá de la versión de `psutil` instalada; su semántica debe verificarse antes de implementar.

### ADP-DEC-006 — Velocidad no informada y campos enteros

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Decisión:** `speed_mbps` será `0` si el sistema no informa la velocidad; `mtu` y `speed_mbps` se tratan como enteros en el contrato.

## Pendientes de decisión

### ADP-PEND-001 — Saturación del semáforo

Definir si la solicitud adicional espera o recibe HTTP 429; el requisito de un solo worker para que el semáforo sea global está fijado en ADP-DEC-004.

### ADP-PEND-002 — Errores y datos parciales

Definir la política de API ante fallos de psutil, un adaptador con datos incompletos o una consulta parcial del sistema.

### ADP-PEND-003 — Soporte de multicast

Verificar que la versión de `psutil` instalada exponga la bandera de multicast en `net_if_stats()` y definir el valor a devolver cuando no esté disponible.