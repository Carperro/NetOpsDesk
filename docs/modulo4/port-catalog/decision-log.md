# Registro de decisiones — Catálogo de puertos y protocolos

Este registro contiene decisiones específicas de la herramienta 19 aprobadas por el usuario. La existencia de este documento no implica que la herramienta esté implementada.

## Decisiones aprobadas

### PORT-DEC-01 — Dataset local y comportamiento de búsqueda

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Se necesita consultar puertos y protocolos conocidos sin acceder a una fuente remota durante cada búsqueda.
- **Decisión:** El dominio `netops_desk/port_catalog.py` contendrá un dataset estático local con al menos 20 registros comunes de TCP/UDP. Permitirá buscar por número de puerto o nombre de servicio, sin distinguir mayúsculas/minúsculas y con coincidencia parcial. Una consulta vacía devolverá el catálogo completo.
- **Motivo:** Mantener la operación de lectura rápida, local y predecible, con una lógica de filtrado pura.
- **Alternativas:** No registradas.
- **Consecuencias:** El dataset inicial y su procedencia deberán ser revisables. No se eligió una fuente externa ni un proceso de actualización automática.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 19.

### PORT-DEC-02 — Semáforo de concurrencia

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** Aplicar un límite de concurrencia consistente con herramientas del proyecto.
- **Decisión:** La capa API usará `asyncio.Semaphore(5)`.
- **Motivo:** Limitar la cantidad de búsquedas procesadas simultáneamente.
- **Alternativas:** No registradas.
- **Consecuencias:** El semáforo es local al proceso/event loop. No se definieron la respuesta ante saturación ni la garantía global con múltiples workers; esos aspectos no se consideran aprobados por esta decisión.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 19.

## Pendientes

- Definir el conjunto exacto de registros iniciales y sus fuentes.
- Definir orden de resultados, normalización de espacios y si las coincidencias parciales numéricas aplican a los números de puerto.
- Definir política común de errores del Módulo 4 y comportamiento al agotarse el semáforo.
