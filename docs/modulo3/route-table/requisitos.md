# Requisitos — Visor de tabla de rutas

> Estado: especificación documental para la herramienta 14; no describe implementación de esta herramienta.

## Propósito y alcance

- **Módulo y número de catálogo:** Módulo 3, herramienta 14.
- **Propósito:** mostrar la tabla de rutas IPv4 local de Windows con sus destinos y métricas.
- **Incluye:** consulta GET sin parámetros de las rutas IPv4 representables con destino, máscara, gateway IPv4, interfaz IPv4 y métrica.
- **No incluye:** modificar rutas, añadir parámetros de filtrado ni consultar la tabla IPv6.
- **Familias/protocolos admitidos:** IPv4 mediante `route print -4`.

Las filas `On-link` se omiten en v1, conforme a una de las representaciones autorizadas para esta herramienta. Por ello, la respuesta contiene las rutas que cumplen el esquema de gateway IPv4 y no necesariamente todas las filas impresas por Windows.

## Requisitos funcionales

| ID | Requisito | Entrada/condición | Resultado observable | Estado |
|---|---|---|---|---|
| RT-F-001 | Consultar rutas IPv4 locales | GET sin parámetros ni body | Se consulta la tabla de rutas IPv4 del servidor | Aprobado |
| RT-F-002 | Mostrar las rutas reconocidas | Salida de `route print -4` | Cada ruta incluye destino, máscara, gateway, interfaz y métrica | Aprobado |
| RT-F-003 | Omitir rutas `On-link` | Fila no contiene un gateway IPv4 | La fila no aparece en `routes` | Aprobado como representación v1 |
| RT-F-004 | Reutilizar el trabajo de Route Analyzer | Ya existe parser/adaptador para `route print -4` en herramienta 10 | Se reutiliza el adaptador o su patrón de parsing sin acoplar el nuevo dominio al dominio de Route Analyzer | Aprobado como directiva arquitectónica; mecanismo concreto al implementar |

## Requisitos no funcionales

| ID | Área | Requisito y límite | Criterio de aceptación | Estado |
|---|---|---|---|---|
| RT-NF-001 | Recursos | Timeout de 10 segundos para la ejecución del comando | El proceso no queda ejecutándose indefinidamente | Aprobado |
| RT-NF-002 | Concurrencia | `asyncio.Semaphore(5)` global | Máximo de cinco consultas concurrentes en el despliegue acordado | Aprobado; requiere un worker para alcance global |
| RT-NF-003 | Seguridad | Comando fijo, argumentos separados y `shell=False`; no hay parámetros del cliente | La solicitud no puede alterar el comando ejecutado | Aprobado |
| RT-NF-004 | Robustez | Parseo por estructura numérica, independiente de encabezados localizados | Filas se reconocen por cuatro tokens con forma IPv4 y métrica numérica final; las direcciones se validan como IPv4 antes de emitirlas | Aprobado como objetivo basado en parser existente |

## Criterios de aceptación

- `GET /api/v1/tools/route-table/execute` se ejecuta sin body ni parámetros y devuelve HTTP 200 en caso exitoso.
- Cada elemento de `routes` tiene `destination`, `netmask`, `gateway`, `interface` y `metric` con sus tipos correspondientes.
- Las filas `On-link` se omiten; no se fabrican gateways IPv4 para ellas.
- Se admiten filas que contienen cuatro campos IPv4 (destino, máscara, gateway, interfaz) y una métrica numérica final.
- El runner usa `route print -4`, `shell=False` y timeout de 10 segundos; no recibe argumentos del cliente.

## Fuentes y pendientes

- **Decisiones aplicables:** solicitud explícita del usuario para la herramienta 14.
- **Fuentes técnicas verificadas:** parser de [Route Analyzer](../../modulo2/route-analyzer/arquitectura.md) y `src/netops_desk/route_analyzer.py` (`_parse_route_table`); el regex efectivo reconoce cuatro tokens con forma IPv4 y un entero final. La validación de rangos de octetos corresponde al dominio nuevo.
- **Pendiente de aprobación o investigación:** política HTTP para fallos y timeout; política de saturación del semáforo; límite de bytes para stdout; orden garantizado de las rutas; semántica ante tabla vacía o salida parcial.
