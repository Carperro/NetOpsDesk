# Registro de decisiones — Detector de solapamiento

No se identificaron decisiones aprobadas específicas de la herramienta en las fuentes revisadas. Los comportamientos presentes en el código y las pruebas se describen como implementación observada en los demás documentos; no se convierten por sí solos en decisiones de producto.

## Decisiones globales aplicables

- **DEC-011 — Alcance del MVP:** Overlap forma parte de las 25 herramientas del MVP. Fuente: [`docs/fundacional/decision-log.md`](../../fundacional/decision-log.md).
- **DEC-012 — Contrato común de errores HTTP:** aplica el sobre JSON común y la semántica compartida de estados HTTP. Fuente: [`docs/fundacional/decision-log.md`](../../fundacional/decision-log.md).
- **DEC-013 — Presentación segura de datos dinámicos:** usar APIs de nodos y `textContent`/propiedades de formulario; no interpolar datos no confiables en HTML. Fuente: [`docs/fundacional/decision-log.md`](../../fundacional/decision-log.md).

## Decisiones específicas aprobadas

### OVL-DEC-001 — Límite de redes por solicitud

- **Estado:** APROBADA.
- **Contexto:** Overlap compara todos los pares de redes, por lo que el número de comparaciones crece cuadráticamente con el tamaño de la entrada.
- **Decisión:** admitir entre 2 y 50 redes por solicitud.
- **Motivo:** acotar el coste de comparación y el volumen de resultados.
- **Consecuencias:** más de 50 redes se rechazan con HTTP 422 y `invalid_network`.

## Otras decisiones específicas pendientes
- Resolver la discrepancia del título y encabezado que identifican la página de Overlap como “Planificador VLSM”. Este documento no autoriza un cambio de código.
