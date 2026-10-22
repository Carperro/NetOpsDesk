# Arquitectura — Asistente de configuración IP

> Estado: arquitectura objetivo basada en el alcance aprobado; no describe componentes implementados.

## Componentes y responsabilidades

| Capa/componente | Ubicación | Responsabilidad | Dependencias permitidas |
|---|---|---|---|
| Dominio | `src/netops_desk/ip_config.py` | Validar parámetros conforme a reglas aprobadas y generar comando y explicación como datos para las cuatro acciones | Biblioteca estándar; no importa FastAPI, subprocess ni módulos del navegador |
| Modelos y API | Ubicaciones por determinar al implementar | Validar el request y adaptar la operación al dominio | FastAPI/Pydantic y dominio |
| Interfaz | Integración frontend por determinar | Mostrar formulario según acción, presentar comando como texto y ofrecer copiar | API y recursos locales |
| Pruebas | Archivos por determinar al implementar | Verificar generación, validación, contrato HTTP y comportamiento de copia | Pytest y dobles cuando sean útiles |

## Flujo principal

1. La interfaz solicita la acción y muestra únicamente los campos correspondientes.
2. La API valida estructura y tipos, y llama al dominio.
3. El dominio requiere `interface_name` para toda acción; valida los campos adicionales requeridos y rechaza nombres de interfaz con comillas dobles, backticks o caracteres de control.
4. El dominio genera el comando aprobado para `renew_dhcp`, `set_dhcp`, `set_static` o `set_dns`, junto con su explicación; no ejecuta el comando.
5. La API devuelve los datos generados según el contrato que se formalice.
6. La interfaz inserta el comando como texto y, a solicitud de la persona, lo copia al portapapeles.

## Límites y errores

- **Validación en interfaz:** puede guiar la entrada, pero no sustituye la validación de API y dominio.
- **Validación API/dominio:** debe validar acción, presencia de campos por acción, valores IP y `interface_name`. El dominio rechaza en `interface_name` comillas dobles, backticks y caracteres de control; el contrato traduce los casos definidos a HTTP 422.
- **Errores y advertencias:** los códigos HTTP y el sobre de error del Módulo 3 deben definirse en el contrato común aplicable; no se asume automáticamente que DEC-012 del Módulo 1 rija este módulo.
- **Recursos y seguridad:** el comando contiene datos del cliente y puede tener efectos importantes si se ejecuta manualmente. Aplicar las validaciones aprobadas antes de interpolar valores; mostrarlo como texto, nunca como HTML. No usar `subprocess`, `shell` ni mecanismos equivalentes.

## Decisiones estructurales y evolución

- **Decisiones aprobadas:** generación de comandos en texto plano sin ejecución en el servidor; `interface_name` obligatorio en todas las acciones; acciones `renew_dhcp`, `set_dhcp`, `set_static` y `set_dns`; rechazo de comillas dobles, backticks y controles en el nombre.
- **Alternativas descartadas:** ejecución automática en el servidor, expresamente fuera del alcance.
- **Dependencias de plataforma/conectividad:** los comandos generados están destinados a Windows CMD/Netsh; la herramienta no necesita conectividad ni consultar el sistema local.
- **Límites que permiten evolución futura:** dominio independiente del transporte e interfaz; no se introduce infraestructura de ejecución de procesos.

## Sintaxis aprobada

- `renew_dhcp`: `ipconfig /renew "{interface_name}"`
- `set_dhcp`: `netsh interface ip set address name="{interface_name}" source=dhcp`
- `set_static`: `netsh interface ip set address name="{interface_name}" static {ip} {mask} {gateway}`
- `set_dns`: `netsh interface ip set dns name="{interface_name}" static {dns_ip}`

Los valores se insertan únicamente después de validar su tipo y formato. En `interface_name` se rechazan comillas dobles, backticks y caracteres de control. La interfaz de usuario presenta la cadena como texto y copiarla no la ejecuta.

## Pendientes de diseño

- Definir y aprobar el esquema de respuesta exitosa y el tratamiento de campos adicionales.
- Formalizar estados y sobre para errores distintos de los cuatro códigos HTTP 422 aprobados.
- Confirmar si la máscara debe limitarse a valores IPv4 contiguos según el contrato de implementación.
