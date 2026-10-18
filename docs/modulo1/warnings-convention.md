# Convención actual de advertencias y normalización

Este documento registra los mecanismos de advertencia que usan actualmente las herramientas del Módulo 1. No los unifica ni cambia sus contratos.

| Herramienta | Mecanismo actual | Significado |
|---|---|---|
| Calculadora IPv4/CIDR | `warnings: [{code, message}]` | Informa normalización de bits de host y aplicación del modo `point-to-point`. |
| Subnetting IPv4 | `was_normalized: bool` | Indica si la dirección de entrada se normalizó a la red; no incluye código ni mensaje. |
| VLSM IPv4 | Sin flag ni colección de warnings | Normaliza la red base y devuelve `base_network` normalizada. |
| Overlap IPv4 | Conserva la entrada original en `networks` | La salida permite ver el texto recibido; las redes comparadas se normalizan internamente. No hay campo de advertencias. |
| Calculadora IPv6 | `host_bits_set: bool` y `warnings: [{code, message}]` | El contrato aprobado adopta el patrón de advertencia estructurada de IPv4 y además expone el indicador booleano. Véase [`ipv6-calculator/api-contracts.md`](ipv6-calculator/api-contracts.md). |

Una convergencia de estos mecanismos en una versión futura requerirá una decisión explícita de compatibilidad con los clientes que consumen los contratos actuales. Esta documentación no autoriza cambios de respuesta ni de interfaz.
