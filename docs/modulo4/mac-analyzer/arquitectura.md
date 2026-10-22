# Arquitectura — Analizador de direcciones MAC

> Estado: arquitectura objetivo basada en el alcance aprobado. El catálogo marca la herramienta pendiente de desarrollo e integración; las ubicaciones descritas son destino y no componentes existentes.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/mac_analyzer.py` | Validar y normalizar MAC, invocar el runner inyectado y formar el resultado | Biblioteca estándar y protocolo `MacVendorLookupRunner`; no importa FastAPI ni la biblioteca OUI |
| Modelo y ruta API | Por definir al implementar | Validar el request y adaptar el caso de uso al contrato HTTP | FastAPI/Pydantic, dominio y proveedor del runner |
| Runner/infraestructura | Adaptador de infraestructura por definir | Consultar el fabricante mediante `mac_vendor_lookup.MacLookup().lookup(mac)` usando datos locales | `mac-vendor-lookup` y su base OUI local |
| Interfaz | Integración frontend por definir | Enviar la MAC y presentar entrada, forma normalizada y fabricante | API y recursos locales |
| Pruebas | Archivos por definir al implementar | Verificar validación, normalización, consulta del runner y contrato HTTP | Pytest, runner falso y cliente de API |

## Flujo principal

1. La interfaz envía `POST /api/v1/tools/mac-analyzer/execute` con el campo `mac`.
2. La API valida el tipo y la estructura del request.
3. El dominio conserva el texto original, verifica seis octetos hexadecimales separados por dos puntos o guiones, y normaliza a minúsculas con dos puntos.
4. El dominio entrega la MAC normalizada al `MacVendorLookupRunner` inyectado.
5. El runner invoca `MacLookup().lookup(mac)` contra la base local; si no hay fabricante, devuelve `Desconocido`.
6. El dominio devuelve `mac_original`, `mac_normalized` y `vendor`; la API serializa la respuesta.

## Límites y errores

- **Validación en interfaz:** puede advertir sobre el formato, pero no sustituye la validación de API y dominio.
- **Validación API/dominio:** admitir únicamente seis octetos hexadecimales en los formatos separados por `:` o `-` aprobados. No ampliar silenciosamente a formatos compactos o con puntos.
- **Errores y advertencias:** la validación fallida produce `DomainError(code="invalid_mac")`; el handler global lo traduce a HTTP 422. La saturación del semáforo se rechaza con HTTP 429 y código `too_many_requests`.
- **Recursos y seguridad:** usar la copia OUI local; no consultar un proveedor remoto ni transmitir la dirección del usuario. La base es finita, pero su versión y actualización requieren definición operativa.

## Concurrencia y evolución

La capa API utilizará `asyncio.Semaphore(5)` y rechazará inmediatamente con HTTP 429 `too_many_requests` cuando los cinco permisos estén ocupados. El semáforo es local al proceso/event loop y no coordina varios workers; por eso, el límite descrito aplica por proceso salvo que el despliegue use un único worker o incorpore coordinación compartida.

La dependencia de fabricante queda detrás del runner, de modo que el dominio y sus pruebas no quedan acoplados a `mac-vendor-lookup`. El paquete contiene la copia local de datos OUI y su actualización se delega a las actualizaciones del paquete mediante `pip`; no se requiere lógica de actualización dentro de NetOps Desk. La tarea de implementación deberá declarar y fijar la dependencia conforme al proceso de gestión de dependencias del proyecto.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** dominio con runner inyectado; consulta de fabricante mediante `mac-vendor-lookup`; fabricante no encontrado representado como `Desconocido`; consulta offline (DEC-019).
- **Alternativas descartadas:** consulta obligatoria a un servicio remoto para resolver fabricantes.
- **Dependencias de plataforma/conectividad:** la operación no necesita conectividad externa; depende de la copia local de datos OUI.
- **Límites que permiten evolución futura:** el dominio depende de una interfaz pequeña; el runner puede sustituirse o actualizarse sin introducir la biblioteca en reglas de negocio.

## Referencias

- [Requisitos](requisitos.md), [contrato API](api-contracts.md), [decisiones](decision-log.md) y [estrategia de pruebas](test-strategy.md).
- [Catálogo fundacional, herramienta 18](../../fundacional/catalogo.md).
- [Contrato común de API del Módulo 1](../../modulo1/api-contracts.md), como referencia de sobre de error; la política transversal del Módulo 4 sigue pendiente.
