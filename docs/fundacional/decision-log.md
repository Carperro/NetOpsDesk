# Registro global de decisiones — NetOps Desk

Este documento es la fuente canónica de decisiones aprobadas que afectan al producto, a más de una herramienta o a la gobernanza del proyecto. Las decisiones específicas de una herramienta permanecen en el registro de esa herramienta. Las entradas globales también se conservan en su registro histórico de origen cuando corresponde; esta copia gobierna su vigencia transversal.

## DEC-011 — Alcance del MVP

- **Estado:** APROBADA
- **Contexto:** El alcance del MVP se amplía desde las tres primeras herramientas del Módulo 1 a las 25 herramientas del catálogo oficial.
- **Decisión:** Las 25 herramientas de `docs/fundacional/catalogo.md` forman parte del MVP. El MVP no se considera terminado hasta que las 25 herramientas estén desarrolladas e integradas con la interfaz frontend. El desarrollo y la documentación avanzan progresivamente por herramienta; la documentación de funcionamiento, arquitectura y estrategia de pruebas se completa al terminar la integración frontend de cada herramienta.
- **Motivo:** Decisión expresa del usuario.
- **Vigencia y alcance:** Amplía DEC-009 y DEC-010 y sustituye cualquier límite que restrinja el MVP a las herramientas 1, 2 o 3. En lo que contradiga la inclusión de las 25 herramientas, sustituye las exclusiones de DEC-003 relativas a diagnósticos del sistema operativo, inventario, IPAM, historial y persistencia necesaria para esas herramientas. No aprueba autenticación completa, acceso por LAN ni una tecnología concreta de persistencia. La pertenencia al MVP, el estado de implementación/despliegue y el estado documental se registran por separado.
- **Origen histórico:** `docs/modulo1/ipv4-calculator/decision-log.md`.

## DEC-012 — Contrato común de errores HTTP

- **Estado:** APROBADA
- **Contexto:** Los contratos del Módulo 1 describían de manera desigual los errores HTTP y el formato de error; el dominio debe permanecer independiente del transporte HTTP.
- **Decisión:** Los contratos del Módulo 1 comparten el sobre JSON `{ "error": "<código>", "detail": "<mensaje>" }`. Los errores de validación y dominio usan HTTP 422; los errores de sintaxis JSON conservan la semántica de DEC-007; los tipos de contenido no admitidos usan HTTP 415; las excepciones inesperadas usan HTTP 500 con detalle seguro. Cada herramienta conserva sus rutas, datos y códigos específicos.
- **Motivo:** Unificar el contrato público y traducir errores en la capa API sin introducir dependencias HTTP en el dominio.
- **Consecuencias:** `docs/modulo1/api-contracts.md` define las reglas comunes; cada contrato de herramienta define sus particularidades. En la revisión del 2026-10-18, las cuatro herramientas implementadas usan 422 para validación y dominio, 415 para tipos de contenido no admitidos y mensajes de usuario en español. DEC-007 sigue vigente para errores relacionados con el cuerpo JSON.
- **Origen histórico:** `docs/modulo1/ipv4-calculator/decision-log.md`.

## DEC-013 — Presentación segura de datos dinámicos

- **Estado:** APROBADA
- **Contexto:** Los frontends de Overlap y VLSM insertaban mensajes de error y otros valores dinámicos mediante `innerHTML`. En Overlap, el detalle de error puede contener texto derivado de una red inválida suministrada por el usuario. La revisión estática identificó un flujo de riesgo de inyección HTML; no se afirmó explotación dinámica demostrada.
- **Decisión:** En Overlap y VLSM, construir elementos dinámicos del DOM mediante APIs de nodos y presentar mensajes, valores de entrada y datos de respuesta con `textContent` o propiedades de formulario como `value`. No interpolar datos dinámicos en plantillas HTML interpretadas.
- **Motivo:** Evitar que datos de entrada, respuestas o errores se interpreten como marcado o código ejecutable y seguir el principio de presentación segura de datos no confiables.
- **Consecuencias:** Se aplica a `src/netops_desk/static/js/overlap.js` y `src/netops_desk/static/js/vlsm.js`; se añadieron guardas estáticas en `tests/test_frontend_static.py`. No cambia contratos, rutas ni mensajes de dominio. La decisión no registra pruebas dinámicas de explotación o navegador.
- **Origen histórico:** `docs/modulo1/ipv4-calculator/decision-log.md`.

## DEC-014 — Aprobación de AGENTS.md

- **Estado:** APROBADA
- **Fecha:** 2026-10-18
- **Contexto:** `AGENTS.md` contenía la marca «Propuesta para aprobación» pese a ser utilizado como conjunto de instrucciones operativas del repositorio.
- **Decisión:** El usuario aprueba formalmente `AGENTS.md` como directiva vigente para agentes que trabajen en NetOps Desk, subordinada a instrucciones explícitas y recientes del usuario y a las decisiones que este apruebe. La marca de estado del archivo deberá reflejar esta aprobación.
- **Motivo:** Hacer explícito el estado de aprobación de las reglas de trabajo y evitar ambigüedad sobre su vigencia.
- **Consecuencias:** `AGENTS.md` conserva su jerarquía y límites de autorización; su aprobación no amplía el alcance de una tarea ni reemplaza las autorizaciones específicas requeridas por el usuario.
- **Aprobación:** Instrucción explícita del usuario en la sesión del 2026-10-18.

## DEC-015 — Herramienta y política de lockfile de dependencias

- **Estado:** APROBADA
- **Fecha:** 2026-10-18
- **Contexto:** El proyecto declaraba rangos mínimos de dependencias en `pyproject.toml`, pero no tenía lockfile. `uv` no está disponible en el entorno de trabajo.
- **Decisión:** Usar `pip-tools` para compilar `requirements.lock` desde `pyproject.toml`, incluyendo los extras `test` y `dev`, con hashes y fijando también dependencias consideradas inseguras por pip (`pip` y `setuptools`). `pip-tools` y `pre-commit` forman parte del extra `dev`; el lockfile se regenera con `pip-compile --extra test --extra dev --generate-hashes --allow-unsafe --strip-extras --output-file requirements.lock pyproject.toml` y el entorno se sincroniza con `pip-sync requirements.lock`.
- **Motivo:** Fijar las dependencias usadas por pruebas y desarrollo y contar con un procedimiento repetible para actualizar el lockfile. La elección de `pip-tools` sigue la alternativa indicada para el caso en que `uv` no esté instalado.
- **Consecuencias:** `requirements.lock` registra las versiones resueltas y sus hashes para Python 3.12. Los cambios intencionales en dependencias requieren actualizar `pyproject.toml`, regenerar el lockfile y revisar ambos diffs juntos. El lockfile no sustituye la declaración de dependencias del proyecto.
- **Aprobación:** Autorización explícita del usuario para ejecutar F4 el 2026-10-18.

## DEC-020 — SQLite nativo, patrón Repository y autenticación JWT

- **Estado:** APROBADA
- **Contexto:** NetOps Desk requiere persistencia local compartida para usuarios, inventario, IPAM e historial. Las herramientas deben mantener separados el dominio, la API y el acceso a datos; las rutas de herramientas deben exigir autenticación.
- **Decisión:** Usar SQLite mediante `sqlite3` nativo, sin ORM, sobre `netops.db` en el directorio de trabajo desde el que se inicia la aplicación, y encapsular el acceso mediante repositorios. Configurar las conexiones con WAL y `busy_timeout=5000`; traducir `sqlite3.OperationalError` a `DomainError(code="db_locked")`. Autenticar con JWT Bearer (PyJWT/HS256) y hashes Argon2 gestionados por `pwdlib`; crear `admin`/`admin` solo al inicializar una base vacía.
- **Motivo:** Mantener una instalación local sin servicio de base de datos externo, compartir persistencia entre herramientas y conservar el dominio independiente de SQLite y HTTP.
- **Alternativas consideradas:** SQLAlchemy/ORM y base de datos de servidor. No se adoptan para esta entrega.
- **Consecuencias:** Las rutas de herramientas y `/api/v1/auth/me` requieren un token; el login permanece público. WAL mejora la convivencia entre lectores y escritores, pero SQLite sigue permitiendo un único escritor a la vez. La cuenta inicial y la clave JWT de desarrollo deben sustituirse antes de una entrega operativa.
- **Aprobación:** Solicitud explícita del usuario para documentar la decisión global de SQLite, Repository y JWT; persistencia SQLite nativa aprobada previamente como DEC-018.
- **Referencias:** [DEC-018 de Inventario](../modulo4/inventory/decision-log.md#dec-018--persistencia-sqlite-nativa-con-patrón-repository), [decisiones de autenticación](auth/decision-log.md).
