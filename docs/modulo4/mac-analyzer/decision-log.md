# Registro de decisiones — Analizador de direcciones MAC

Este registro contiene decisiones específicas de la herramienta 18. La existencia de estas decisiones y documentos no implica que la herramienta esté implementada.

## Decisiones aprobadas

### DEC-019 — Uso de `mac-vendor-lookup` para identificación offline de fabricantes OUI

- **Estado:** APROBADA por instrucción explícita del usuario.
- **Fecha:** 2026-10-20.
- **Contexto:** La herramienta 18 debe asociar una MAC con un fabricante cuando exista información OUI disponible; una consulta remota enviaría datos fuera de la aplicación y requeriría conectividad.
- **Decisión:** Usar la biblioteca `mac-vendor-lookup`, que contiene una copia local de la lista OUI de IEEE, detrás de un `MacVendorLookupRunner` inyectado al dominio. Consultar el fabricante mediante `mac_vendor_lookup.MacLookup().lookup(mac)`; cuando no se encuentre, devolver `Desconocido`.
- **Motivo:** Permitir identificación de fabricante sin depender de Internet y mantener la dependencia externa fuera de las reglas del dominio.
- **Alternativas:** Consulta a un servicio remoto; descartada para este alcance offline. No se registraron otras alternativas.
- **Consecuencias:** La dependencia deberá declararse y fijarse antes de implementar. La versión y fecha de los datos OUI, y su procedimiento de actualización, deben ser visibles y verificables. Esta documentación no instala ni añade la dependencia.
- **Aprobación:** Instrucción explícita del usuario al solicitar la documentación de la herramienta 18, 2026-10-20.

## Pendientes de decisión

### MAC-PEND-001 — Error de validación y contrato común

Definir el código HTTP y el código estable para una MAC inválida. Se propone `invalid_mac` con HTTP 422, siguiendo la convención general de errores de dominio, pero no fue especificado expresamente en la decisión de alcance.

### MAC-PEND-002 — Saturación y alcance del semáforo

Está aprobado `asyncio.Semaphore(5)`. Falta definir si una solicitud adicional espera o responde HTTP 429 y si el despliegue garantiza un único worker para que el límite sea global.

### MAC-PEND-003 — Ciclo de vida de la base OUI

Definir cómo se verifica la antigüedad de la copia local y cómo se actualiza la lista sin introducir consultas de red durante el uso de la herramienta.
