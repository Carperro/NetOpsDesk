# Catálogo oficial de herramientas - NetOps Desk

El catálogo del producto contempla **25 herramientas distribuidas en cinco módulos**. Representa el alcance previsto a largo plazo, no el estado actual de desarrollo.

La implementación es gradual. El primer módulo prioriza herramientas de direccionamiento IP; el resto del catálogo se incorpora a medida que se valida el enfoque.

## Estado actual

**MVP implementado:** Módulo 1, herramientas 1 (Calculadora IPv4/CIDR), 2 (Subnetting IPv4) y 3 (Planificador VLSM).

Las herramientas 4 a 25 están previstas y no se marcan como implementadas. El alcance aprobado del MVP está registrado en `docs/modulo1/ipv4-calculator/decision-log.md`; cada herramienta implementada mantiene sus documentos en el directorio correspondiente de `docs/modulo1/`.

## Módulo 1. Direccionamiento IP y subnetting

### 1. Calculadora IPv4/CIDR *(MVP — implementada)*
- Dirección IP y prefijo.
- Dirección de red y broadcast.
- Máscara de subred.
- Rango de hosts.
- Cantidad de direcciones y hosts utilizables.

### 2. Subnetting IPv4 *(MVP — implementada)*
- División de redes por prefijos.
- Cálculo según cantidad de hosts requerida.
- Visualización de las subredes resultantes.

### 3. Planificador VLSM *(MVP — implementada)*
- Asignación de subredes de distintos tamaños.
- Organización según las necesidades de hosts.
- Detección de asignaciones inválidas.

### 4. Detector de solapamiento de redes *(prevista)*
- Comparación de rangos CIDR.
- Identificación de redes que se superponen.
- Explicación del conflicto.

### 5. Calculadora IPv6 *(prevista)*
- Dirección y prefijo.
- Dirección de red y rangos.
- Tipos de direcciones.
- Datos derivados de la dirección y el prefijo.

## Módulo 2. Diagnóstico de conectividad

### 6. Ping *(prevista)*
- Tiempo de respuesta.
- Latencia.
- Pérdida de paquetes.
- Resultado del diagnóstico.

### 7. Traceroute *(prevista)*
- Saltos de la ruta.
- Direcciones que respondieron.
- Tiempos de respuesta cuando estén disponibles.

### 8. Prueba de puertos TCP *(prevista)*
- Comprobación de conectividad TCP hacia un host y puerto.
- Tiempo de espera configurable.
- Diferenciación entre conexión exitosa, rechazo y ausencia de respuesta cuando pueda determinarse.

### 9. Diagnóstico DNS *(prevista)*
- Consultas de registros DNS.
- Comparación de resolvers.
- Análisis de problemas de resolución.

### 10. Analizador de gateway y rutas *(prevista)*
- Identificación de la puerta de enlace.
- Consulta de rutas relevantes.
- Explicación básica de cómo se selecciona una ruta.

## Módulo 3. Diagnóstico local de Windows

### 11. Información de interfaces de red *(prevista)*
- Dirección IP.
- Máscara o prefijo.
- Gateway.
- DNS.
- Estado del adaptador.

### 12. Asistente de configuración IP *(prevista)*
- Preparación y explicación de comandos DHCP y DNS.
- Ayuda para renovar la configuración.
- Instrucciones claras sobre el efecto de cada comando.

### 13. Visor de caché ARP *(prevista)*
- Direcciones IP conocidas.
- Direcciones MAC asociadas.
- Interfaz y otros datos disponibles.

### 14. Visor de tabla de rutas *(prevista)*
- Consulta de rutas locales.
- Métricas y gateways cuando estén disponibles.
- Explicación de las entradas relevantes.

### 15. Estado de adaptadores *(prevista)*
- Estado del enlace.
- Velocidad cuando el sistema la informe.
- Información disponible sobre los adaptadores.

## Módulo 4. Inventario y planificación de redes

### 16. Inventario de dispositivos *(prevista)*
- Nombre.
- Dirección IP.
- Tipo de equipo.
- Ubicación.
- Observaciones.

### 17. Gestor de direcciones IP *(prevista)*
- Registro de asignaciones conocidas.
- Consulta de direcciones utilizadas.
- Detección de duplicados dentro del inventario almacenado.

### 18. Analizador de direcciones MAC *(prevista)*
- Validación de formato.
- Normalización.
- Identificación del fabricante cuando exista una base OUI local adecuada.

### 19. Catálogo de puertos y protocolos *(prevista)*
- Puertos conocidos.
- Protocolos asociados.
- Descripciones y usos habituales.

### 20. Calculadora MTU y fragmentación *(prevista)*
- Cálculo de tamaños de paquetes.
- Sobrecarga de cabeceras según los parámetros elegidos.
- Explicación de la fragmentación y sus límites.

## Módulo 5. Análisis, documentación y productividad

### 21. Generador de informes de diagnóstico *(prevista)*
- Consolidación de resultados.
- Registro de parámetros y errores.
- Exportación a un formato que se definirá durante el diseño.

### 22. Asistente de resolución de problemas *(prevista)*
- Recopilación de síntomas y resultados.
- Presentación de posibles causas.
- Propuesta de comprobaciones siguientes.

### 23. Comparador de configuraciones *(prevista)*
- Comparación de dos configuraciones.
- Identificación de diferencias.
- Presentación clara de los cambios detectados.

### 24. Generador de comandos *(prevista)*
- Preparación de comandos.
- Explicación de sus parámetros.
- Advertencias cuando puedan modificar el sistema o requerir privilegios.

### 25. Historial de diagnósticos *(prevista)*
- Registro de ejecuciones.
- Fecha y resultado.
- Consulta de diagnósticos anteriores.
