# Registro de decisiones — Planificador VLSM

Este registro describe decisiones autorizadas para la implementación actual del Planificador VLSM. La inclusión de la herramienta en el MVP está registrada en `docs/modulo1/ipv4-calculator/decision-log.md` (DEC-010).

## Decisiones aprobadas

### VLSM-DEC-001 — Orden de asignación

- **Estado:** APROBADA.
- **Contexto:** asignación de varios bloques de red a partir de requerimientos de distintos tamaños.
- **Decisión:** ordenar los requerimientos de mayor a menor cantidad de hosts utilizando `sorted()` antes de asignar subredes.
- **Motivo:** asignar primero los bloques más grandes permite ubicarlos antes que los bloques pequeños en el espacio disponible.
- **Consecuencias:** el orden de entrada no determina el orden de asignación; `allocated` refleja el orden descendente por cantidad de hosts.

### VLSM-DEC-002 — Cálculo del espacio restante

- **Estado:** APROBADA.
- **Contexto:** informar el espacio libre después de asignar los bloques requeridos.
- **Decisión:** calcular el intervalo libre como el rango entre la siguiente IP después del último broadcast asignado y el broadcast de la red base. Calcular `total_ips` mediante la diferencia entera entre ambas direcciones, más uno, sin construir una nueva subred.
- **Motivo:** la respuesta representa el rango contiguo restante y su cantidad total de direcciones sin afirmar que ese intervalo sea una subred CIDR alineada.
- **Consecuencias:** `remaining` contiene cero o un elemento con `network`, `broadcast` y `total_ips`; si no hay direcciones disponibles, queda vacío.

### VLSM-DEC-003 — Límite de requerimientos

- **Estado:** APROBADA.
- **Contexto:** cada requerimiento VLSM genera una asignación y trabajo proporcional de validación y cálculo.
- **Decisión:** admitir como máximo 100 requerimientos por solicitud.
- **Motivo:** limitar el tamaño del trabajo y de la respuesta de una operación.
- **Consecuencias:** más de 100 requerimientos se rechazan con HTTP 422 y `invalid_requirement`.

## Alcance

Estas decisiones describen el algoritmo presente en `src/netops_desk/vlsm.py`. Los campos HTTP y las respuestas están documentados en `api-contracts.md`.
