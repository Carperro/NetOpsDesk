# Auditoría documental — estado y hallazgos vigentes

**Última actualización:** 2026-10-18  
**Tipo:** registro de auditoría documental estática; no es fuente normativa del alcance.  
**Fuentes de autoridad:** instrucciones vigentes del usuario, decisiones aprobadas y documentos actuales del proyecto.

## Propósito y uso

Este archivo conserva el inventario y los hallazgos de auditorías documentales anteriores, corregidos conforme a las decisiones posteriores del usuario. Debe servir como contexto para revisar coherencia, no como fuente de decisiones. Para el alcance vigente, consultar el registro de decisiones y el catálogo.

La primera versión de este informe contenía conclusiones que quedaron obsoletas o fueron refutadas. Las correcciones se registran en la sección «Hallazgos reevaluados»; no deben reutilizarse las conclusiones antiguas como estado actual.

## Estado vigente del proyecto

- **CONFIRMADO — MVP:** las 25 herramientas del catálogo forman parte del MVP. El MVP no se considera terminado hasta desarrollar e integrar las 25 con la interfaz frontend. Véase DEC-011 en `docs/modulo1/ipv4-calculator/decision-log.md`.
- **CONFIRMADO — despliegue declarado por el usuario:** Calculadora IPv4/CIDR, Subnetting IPv4, Planificador VLSM y Detector de solapamiento están desplegados.
- **CONFIRMADO — documentación:** Overlap aún no tiene documentación específica. Las herramientas restantes se documentan progresivamente al terminar su integración frontend.
- **CONFIRMADO — API:** DEC-012 establece un contrato común de errores HTTP para el Módulo 1, descrito en `docs/modulo1/api-contracts.md`.
- **CONFIRMADO — límites de actuación:** `AGENTS.md` y el código no se modificaron en las actualizaciones documentales recientes. Su línea de fase y alcance no refleja DEC-011; esa discrepancia requiere tratamiento autorizado independiente.

## Inventario documental actual

El repositorio contiene 19 archivos Markdown bajo `docs/` en esta revisión:

- `docs/fundacional/`: visión y objetivos, catálogo, principios y estándares.
- `docs/modulo1/`: visión del módulo, convenciones comunes de API y carpetas de Calculadora IPv4/CIDR, Subnetting y VLSM.
- `docs/auditoria-documental.md`: este registro.

No existen todavía carpetas de documentación para los módulos 2–5 ni para Overlap. No se crean documentos vacíos: la documentación de cada herramienta se prepara progresivamente después de su integración frontend.

## Hallazgos reevaluados

| ID | Hallazgo inicial | Estado actual y evidencia |
|---|---|---|
| H-01 | README mostraba 115 tests aprobados. | **RESUELTO DOCUMENTALMENTE, resultado de tests DESCONOCIDO.** La insignia fija fue retirada del README. No se ejecutaron pruebas en esta revisión; no se afirma un resultado actual. |
| H-02 | `AGENTS.md` estaba marcado «Propuesta para aprobación». | **VIGENTE COMO TEXTO; aprobación DESCONOCIDA.** La marca sigue en el archivo. No se infiere aprobación por la fase o por cambios posteriores. |
| H-03 | Había código de Overlap sin seguimiento y alcance incierto. | **ACTUALIZADO.** El usuario declaró explícitamente que Overlap está desplegado y forma parte del MVP. `git status` muestra archivos locales de Overlap sin seguimiento; eso no establece su origen. La documentación específica sigue pendiente. |
| H-04 | No existía informe de auditoría en `docs/`. | **SUPERADO.** Este archivo existe en el árbol de trabajo y permanece sin seguimiento en Git. No se infiere que no existan otros informes fuera del repositorio. |
| H-05 | VLSM estaba fuera del MVP. | **REFUTADO.** DEC-010 aprobó VLSM; DEC-011 establece que las 25 herramientas pertenecen al MVP. |
| H-06 | `httpx2` se justificaba por compatibilidad con Python 3.12. | **DOCUMENTADO; verificación técnica DESCONOCIDA.** `pyproject.toml` declara `httpx2` en el extra de pruebas y DEC-008 registra la justificación. No se instaló ni se verificó la compatibilidad en ejecución. |

## Discrepancias y brechas aún abiertas

1. **`AGENTS.md` frente a DEC-011:** `AGENTS.md` conserva un alcance inicial más limitado. No se modificó; no utilizar su texto antiguo para invalidar la decisión posterior del usuario.
2. **DEC-003 frente a DEC-011:** DEC-011 sustituye las exclusiones que contradicen la inclusión de las herramientas del catálogo, incluida la persistencia necesaria para inventario, IPAM e historial. No elige tecnología de persistencia ni aprueba autenticación completa o acceso LAN.
3. **Contrato API frente a implementación:** DEC-012 establece HTTP 422 para errores de validación y dominio; algunas rutas actuales de Subnetting, VLSM y Overlap responden HTTP 400. Es una brecha documentada, no corregida en código.
4. **Documentación de herramientas:** la cobertura de documentación no es uniforme. La herramienta Overlap y las herramientas aún no desarrolladas requieren documentación progresiva según se completen sus integraciones frontend.

## Antecedentes técnicos no verificados dinámicamente

Las auditorías estáticas previas señalaron aspectos técnicos en el uso de `innerHTML`, materialización de subredes, alcance IPv4/IPv6 de Subnetting, límites de VLSM, complejidad del detector Overlap y manejo de errores HTTP. Deben tratarse como asuntos por verificar en tareas técnicas autorizadas; este informe no declara esos hallazgos resueltos ni reproducidos.

No se ejecutaron tests, benchmarks, servidores, pruebas visuales ni comprobaciones dinámicas para actualizar este registro.

## Límites y trazabilidad

- Las etiquetas de estado distinguen declaraciones del usuario, decisiones registradas y observaciones del repositorio.
- Los cambios locales o sin seguimiento no demuestran quién los hizo ni con qué autorización.
- Este informe no reemplaza `docs/modulo1/ipv4-calculator/decision-log.md`, el catálogo ni los contratos específicos.
- Antes de utilizar referencias de línea, verificarlas en la versión actual del archivo.
