# Catálogo oficial de herramientas - NetOps Desk

El MVP de NetOps Desk comprende las **25 herramientas distribuidas en cinco módulos** de este catálogo. Las 25 herramientas están implementadas e integradas con el frontend; los estados de verificación y despliegue se registran por separado.

El primer módulo prioriza herramientas de direccionamiento IP. El catálogo mantiene el estado de implementación de cada herramienta.

## Estado actual

**Alcance del MVP:** las 25 herramientas de este catálogo, según DEC-011 en `docs/modulo1/ipv4-calculator/decision-log.md`.

Las herramientas 1 a 4 están desplegadas según confirmación previa del usuario. Las herramientas 5 a 25 constan como implementadas e integradas; su verificación y despliegue no se infieren. La pertenencia al MVP, el despliegue y el estado de documentación se indican por separado.

### Leyenda de estados de implementación

Los estados son acumulativos: una herramienta solo recibe un nivel si cumple ese nivel y los anteriores. «Pendiente» indica que aún no alcanza el primer nivel.

| Estado | Criterio observable |
|---|---|
| **Implementada** | Existe código para los comportamientos funcionales definidos de la herramienta. |
| **Integrada** | La interfaz de la aplicación permite usar la herramienta y está conectada con su API o mecanismo de ejecución aprobado. |
| **Verificada** | Las pruebas de aceptación pertinentes se ejecutaron después del último cambio funcional y pasaron. |
| **Desplegada** | El usuario confirmó que la herramienta está disponible en el entorno previsto. |

El catálogo registra el nivel más alto alcanzado. La documentación se registra por separado y no se infiere del estado de implementación.

## Módulo 1. Direccionamiento IP y subnetting

### 1. Calculadora IPv4/CIDR *(MVP — implementada · integrada · verificada · desplegada)*
- Dirección IP y prefijo.
- Dirección de red y broadcast.
- Máscara de subred.
- Rango de hosts.
- Cantidad de direcciones y hosts utilizables.

### 2. Subnetting IPv4 *(MVP — implementada · integrada · verificada · desplegada)*
- División de redes por prefijos.
- Cálculo según cantidad de hosts requerida.
- Visualización de las subredes resultantes.

### 3. Planificador VLSM *(MVP — implementada · integrada · verificada · desplegada)*
- Asignación de subredes de distintos tamaños.
- Organización según las necesidades de hosts.
- Detección de asignaciones inválidas.

### 4. Detector de solapamiento de redes *(MVP — implementada · integrada · verificada · desplegada)*
- Comparación de rangos CIDR.
- Identificación de redes que se superponen.
- Explicación del conflicto.

### 5. Calculadora IPv6 *(MVP — implementada · integrada)*
- Dirección y prefijo.
- Dirección de red y rangos.
- Tipos de direcciones.
- Datos derivados de la dirección y el prefijo.

## Módulo 2. Diagnóstico de conectividad

### 6. Ping *(MVP — implementada · integrada)*
- Tiempo de respuesta.
- Latencia.
- Pérdida de paquetes.
- Resultado del diagnóstico.

### 7. Traceroute *(MVP — implementada · integrada)*
- Saltos de la ruta.
- Direcciones que respondieron.
- Tiempos de respuesta cuando estén disponibles.

### 8. Prueba de puertos TCP *(MVP — implementada · integrada)*
- Comprobación de conectividad TCP hacia un host y puerto.
- Tiempo de espera configurable.
- Diferenciación entre conexión exitosa, rechazo y ausencia de respuesta cuando pueda determinarse.

### 9. Diagnóstico DNS *(MVP — implementada · integrada)*
- Consultas de registros DNS.
- Comparación de resolvers.
- Análisis de problemas de resolución.

### 10. Analizador de gateway y rutas *(MVP — implementada · integrada)*
- Identificación de la puerta de enlace.
- Consulta de rutas relevantes.
- Explicación básica de cómo se selecciona una ruta.

## Módulo 3. Diagnóstico local de Windows

### 11. Información de interfaces de red *(MVP — implementada · integrada)*
- Dirección IP.
- Máscara o prefijo.
- Gateway.
- DNS.
- Estado del adaptador.

### 12. Asistente de configuración IP *(MVP — implementada · integrada)*
- Preparación y explicación de comandos DHCP y DNS.
- Ayuda para renovar la configuración.
- Instrucciones claras sobre el efecto de cada comando.

### 13. Visor de caché ARP *(MVP — implementada · integrada)*
- Direcciones IP conocidas.
- Direcciones MAC asociadas.
- Interfaz y otros datos disponibles.

### 14. Visor de tabla de rutas *(MVP — implementada · integrada)*
- Consulta de rutas locales.
- Métricas y gateways cuando estén disponibles.
- Explicación de las entradas relevantes.

### 15. Estado de adaptadores *(MVP — implementada · integrada)*
- Estado del enlace.
- Velocidad cuando el sistema la informe.
- Información disponible sobre los adaptadores.

## Módulo 4. Inventario y planificación de redes

### 16. Inventario de dispositivos *(MVP — implementada · integrada)*
- Nombre.
- Dirección IP.
- Tipo de equipo.
- Ubicación.
- Observaciones.

### 17. Gestor de direcciones IP *(MVP — implementada · integrada)*
- Registro de asignaciones conocidas.
- Consulta de direcciones utilizadas.
- Detección de duplicados dentro del inventario almacenado.

### 18. Analizador de direcciones MAC *(MVP — implementada · integrada)*
- Validación de formato.
- Normalización.
- Identificación del fabricante cuando exista una base OUI local adecuada.

### 19. Catálogo de puertos y protocolos *(MVP — implementada · integrada)*
- Puertos conocidos.
- Protocolos asociados.
- Descripciones y usos habituales.

### 20. Calculadora MTU y fragmentación *(MVP — implementada · integrada)*
- Cálculo de tamaños de paquetes.
- Sobrecarga de cabeceras según los parámetros elegidos.
- Explicación de la fragmentación y sus límites.

## Módulo 5. Análisis, documentación y productividad

### 21. Generador de informes de diagnóstico *(MVP — implementada · integrada)*
- Consolidación de resultados.
- Registro de parámetros y errores.
- Exportación del informe en formato Markdown.

### 22. Asistente de resolución de problemas *(MVP — implementada · integrada)*
- Recopilación de síntomas y resultados.
- Presentación de posibles causas.
- Propuesta de comprobaciones siguientes.

### 23. Comparador de configuraciones *(MVP — implementada · integrada)*
- Comparación de dos configuraciones.
- Identificación de diferencias.
- Presentación clara de los cambios detectados.

### 24. Generador de comandos *(MVP — implementada · integrada)*
- Preparación de comandos.
- Explicación de sus parámetros.
- Advertencias cuando puedan modificar el sistema o requerir privilegios.

### 25. Historial de diagnósticos *(MVP — implementada · integrada)*
- Registro manual de diagnósticos; no captura automáticamente ejecuciones de otras herramientas.
- Fecha y resultado.
- Consulta de diagnósticos anteriores.
