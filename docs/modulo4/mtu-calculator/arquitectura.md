# Arquitectura — Calculadora MTU y fragmentación

> Estado: arquitectura objetivo para la herramienta 20. El catálogo la marca pendiente de desarrollo e integración; las ubicaciones descritas son destino, no componentes existentes.

## Componentes y responsabilidades

| Capa/componente | Ubicación objetivo | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/mtu_calculator.py` | Validar opciones y calcular tamaños de cabecera, espacio de datos y advertencias | Biblioteca estándar; cálculo puro, sin FastAPI, red ni sistema operativo |
| Modelo y ruta API | Por definir al implementar | Validar request, llamar al dominio y serializar resultado | FastAPI/Pydantic y dominio |
| Interfaz | Integración frontend por definir | Presentar formulario, resultado y advertencias | API y recursos locales |
| Pruebas | Archivos por definir al implementar | Verificar fórmulas, límites y contrato HTTP | Pytest y cliente de API |

## Flujo principal

1. La interfaz envía `POST /api/v1/tools/mtu-calculator/calculate` con MTU, versión IP, transporte y túnel.
2. El modelo API aplica defaults y valida tipos/rangos/enumeraciones.
3. La ruta obtiene permiso de `asyncio.Semaphore(5)` y llama directamente al dominio.
4. El dominio calcula los tamaños de cabecera y el espacio restante a partir de reglas deterministas; no crea sockets ni paquetes.
5. El dominio devuelve `mss`, `ip_header_size`, `transport_header_size`, `tunnel_header_size` y `warnings`; la API construye la respuesta.
6. La interfaz muestra los valores numéricos y cada advertencia como texto.

## Límites y errores

- **Validación en interfaz:** ayuda a seleccionar valores permitidos, pero no sustituye la validación API/dominio.
- **Validación API/dominio:** `mtu` debe estar entre `68` y `9000`; las opciones de IP, transporte y túnel pertenecen a los conjuntos cerrados de requisitos.
- **Errores y advertencias:** si las cabeceras acumuladas superan `mtu`, el dominio devuelve `mss: 0` e incluye `packet_too_small`; no lanza error HTTP por este caso. Para `mtu < 576`, agrega `mtu_below_minimum`. El status/código HTTP de entradas fuera del rango y la saturación del semáforo requieren alineación con el contrato común del Módulo 4.
- **Recursos y seguridad:** operación matemática acotada por una solicitud, sin entrada que se use como comando ni dependencia de red/persistencia.

## Modelo de cálculo y perfiles aprobados

- El cálculo es `max(0, mtu - ip_header_size - transport_header_size - tunnel_header_size)`. La cabecera IP interior IPv4 se fija en 20 bytes y la IPv6 en 40; la cabecera TCP base es 20 bytes y la UDP 8 bytes.
- `mss` se conserva como nombre del campo de API por compatibilidad con el catálogo: significa MSS al usar TCP y payload máximo de datos al usar UDP. Técnicamente, MSS es una magnitud TCP; UDP define longitud de datagrama/datos, no una opción MSS. Véanse [RFC 6691](https://www.rfc-editor.org/rfc/rfc6691.html) y [RFC 768](https://www.rfc-editor.org/rfc/rfc768.html).
- `mtu` representa el máximo de bytes del paquete IP que admite el enlace (ejemplo: MTU Ethernet 1500, sin contar la cabecera Ethernet). Se resta el paquete IP interior más las cabeceras de transporte y túnel. Los perfiles de túnel aprobados incluyen una cabecera IP exterior IPv4.

| Túnel | Tamaño | Desglose del perfil aprobado |
|---|---:|---|
| `none` | 0 bytes | Sin overhead de túnel. |
| `gre` | 24 bytes | IPv4 exterior 20 + GRE base 4, sin checksum ni opciones adicionales. |
| `ipsec` | 60 bytes | IPv4 exterior 20 + overhead fijo ESP/Auth 40. |
| `wireguard` | 60 bytes | IPv4 exterior 20 + UDP 8 + WireGuard 32. |

Estos son perfiles fijos del producto, no una estimación dinámica de todas las configuraciones posibles de cada protocolo.

## Límites técnicos pendientes

- El producto fija 68 como límite inferior de entrada tomando como referencia la regla de RFC 791 de que un módulo IPv4 debe poder reenviar un datagrama de 68 octetos sin fragmentarlo nuevamente. El umbral de advertencia 576 se toma de la capacidad de recepción de datagramas IPv4 de RFC 791; no es el mínimo de entrada del producto. Para IPv6, [RFC 8200](https://www.rfc-editor.org/rfc/rfc8200.html) establece un MTU mínimo de enlace de 1280 bytes. El rango común 68–1279 se aceptará por la validación aprobada, pero no cumple ese mínimo de enlace IPv6; queda pendiente decidir si IPv6 debe recibir una advertencia adicional o una validación diferenciada.
- La advertencia `mtu_below_minimum` se aplica cuando `mtu < 576`; los valores por debajo de 68 se rechazan en validación. Si el total de cabeceras excede el MTU, el resultado previo al clamp sería negativo y se representa como `mss: 0` más `packet_too_small`.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** dominio puro en `netops_desk/mtu_calculator.py`; ruta API invoca el dominio; opciones de entrada, perfiles fijos de overhead, `mss` como campo genérico de payload, clamp/advertencias y semáforo de cinco permisos (MTU-DEC-01 a MTU-DEC-05).
- **Alternativas descartadas:** consulta del MTU real mediante sistema operativo o red; uso de persistencia para los cálculos.
- **Dependencias de plataforma/conectividad:** ninguna.
- **Límites que permiten evolución futura:** separar el cálculo puro del transporte permite exponer después la misma lógica desde otra interfaz sin acoplarla a FastAPI.

## Referencias

- [Requisitos](requisitos.md), [contrato API](api-contracts.md), [decisiones](decision-log.md) y [estrategia de pruebas](test-strategy.md).
- [Catálogo fundacional, herramienta 20](../../fundacional/catalogo.md).
- Fuentes técnicas: [RFC 791](https://www.rfc-editor.org/rfc/rfc791.html), [RFC 8200](https://www.rfc-editor.org/rfc/rfc8200.html), [RFC 2784](https://www.rfc-editor.org/rfc/rfc2784.html), [RFC 6691](https://www.rfc-editor.org/rfc/rfc6691.html) y [RFC 768](https://www.rfc-editor.org/rfc/rfc768.html).
