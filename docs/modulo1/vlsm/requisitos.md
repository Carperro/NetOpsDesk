# Requisitos del Planificador VLSM

## Alcance y estado

El Planificador VLSM es la herramienta 3 del Módulo 1 y forma parte del MVP. Recibe una red base IPv4/CIDR y una lista de requerimientos de departamentos; devuelve las subredes asignadas y, cuando queda espacio contiguo, el rango de direcciones restante.

La ruta de API, los campos y los modelos de respuesta se especifican en [`api-contracts.md`](api-contracts.md). La estructura de componentes está en [`arquitectura.md`](arquitectura.md).

## Entradas

- `network_cidr`: cadena con la red base CIDR. El dominio la interpreta con `ipaddress.ip_network(..., strict=False)`, por lo que una dirección con bits de host se normaliza a la dirección de red.
- `requirements`: lista no vacía de requerimientos. Cada elemento contiene `name` y `hosts`.
- En la validación de la API, `name` requiere al menos un carácter y `hosts` debe ser un entero mayor que cero.

La herramienta implementada está limitada a IPv4. Una red IPv6 se rechaza con un error de dominio.

## Asignación VLSM

El dominio ordena los requerimientos de mayor a menor cantidad de hosts mediante `sorted(..., key=..., reverse=True)`. Así se asignan primero los bloques de mayor tamaño.

Para cada requerimiento de `hosts` direcciones de host, el código reserva dos direcciones adicionales para red y broadcast y calcula:

```text
bits_para_direcciones = ceil(log2(hosts + 2))
prefijo = 32 - bits_para_direcciones
```

La subred se crea a partir de la siguiente dirección libre y el prefijo calculado. Si el bloque excede el prefijo de la red base o su broadcast supera el broadcast base, el dominio genera un error. La API transforma ese error de dominio en HTTP 400.

## Espacio restante

Después de cada asignación, el puntero avanza a la dirección siguiente al broadcast de la última subred. Si esa dirección no supera el broadcast de la red base, el resultado incluye un elemento en `remaining` con:

- `network`: primera dirección libre;
- `broadcast`: broadcast de la red base;
- `total_ips`: cantidad total de direcciones del rango, calculada como `int(broadcast_base) - int(network_libre) + 1`.

Si no quedan direcciones, `remaining` es una lista vacía. `total_ips` cuenta direcciones totales, no hosts utilizables.

## Límites de red

La fórmula actual añade dos direcciones al requisito de hosts y aplica la convención de reservar red y broadcast. La implementación no contiene un modo configurable para reinterpretar esa fórmula en `/31` o `/32`; no se documentan reglas punto a punto adicionales para VLSM.
