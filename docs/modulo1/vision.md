# Módulo 1. Direccionamiento IP y subnetting

## Propósito

El módulo 1 de NetOps Desk agrupa herramientas para el cálculo, planificación y diagnóstico de direccionamiento IP.

## Estado actual

**MVP implementado:** herramienta 1, Calculadora IPv4/CIDR; herramienta 2, Subnetting IPv4; y herramienta 3, Planificador VLSM.

Las herramientas 4 y 5 están previstas. El catálogo completo con el estado de cada herramienta está en `docs/fundacional/catalogo.md`.

## Herramientas del módulo

1. **Calculadora IPv4/CIDR** *(MVP — implementada)*.
2. **Subnetting IPv4** *(MVP — implementada)*.
3. **Planificador VLSM** *(MVP — implementada)*.
4. **Detector de solapamiento de redes** *(prevista)*.
5. **Calculadora IPv6** *(prevista)*.

El detalle funcional de cada herramienta está en el catálogo oficial.

## Relación con los objetivos del producto

Las herramientas de este módulo contribuyen al primer objetivo de NetOps Desk: construir una herramienta práctica para tareas de diagnóstico, cálculo y documentación de redes.

- Permiten el cálculo preciso de subredes para diseño y gestión de redes IP.
- Facilitan la planificación de direccionamiento mediante VLSM.
- Ayudan a identificar y resolver conflictos de solapamiento de redes.
- Incorporan progresivamente soporte para IPv6 a medida que el módulo avanza.

## Documentación específica del MVP

La documentación de la calculadora IPv4/CIDR (herramienta 1) está en `docs/modulo1/ipv4-calculator/`:

- `requisitos.md`
- `arquitectura.md`
- `api-contracts.md`
- `decision-log.md`
- `test-strategy.md`

La documentación de Subnetting IPv4 (herramienta 2) está en `docs/modulo1/subnetting/`:

- `requisitos.md`
- `arquitectura.md`
- `api-contracts.md`
- `decision-log.md`

La documentación del Planificador VLSM (herramienta 3) está en `docs/modulo1/vlsm/`:

- `requisitos.md`
- `arquitectura.md`
- `api-contracts.md`
- `decision-log.md`
