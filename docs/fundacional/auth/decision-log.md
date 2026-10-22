# Registro de decisiones — Autenticación y login

## AUTH-DEC-01 — JWT Bearer para autenticar la API

- **Estado:** Implementada conforme a la dirección aprobada por el usuario.
- **Decisión:** El login emite JWT firmado con HS256; `/api/v1/auth/me` y las rutas de herramientas validan Bearer tokens. El login queda público.
- **Motivo:** Permite la autenticación solicitada y protege las operaciones de herramientas en el servidor.
- **Consecuencias:** El token dura ocho horas. El cierre de sesión local no revoca un token ya emitido. Cambiar la clave invalida tokens firmados anteriormente.

## AUTH-DEC-02 — Hash Argon2 mediante pwdlib

- **Estado:** Implementada; el repositorio declara `pwdlib[argon2]`.
- **Decisión:** Guardar hash de contraseña generado/verificado con `pwdlib` y Argon2. No usar Passlib/bcrypt en esta implementación.
- **Motivo:** Evita guardar contraseñas en claro y elimina el límite de 72 bytes asociado a bcrypt.
- **Consecuencias:** El esquema de hash debe seguir verificándose frente a la versión de `pwdlib` fijada por el proyecto.

## AUTH-DEC-03 — SQLite compartido y usuario inicial

- **Estado:** Implementada.
- **Decisión:** Mantener usuarios en `netops.db`; crear `admin` con contraseña `admin` al inicializar una base sin usuarios.
- **Motivo:** Habilitar uso local inmediato y reutilizar la persistencia SQLite del proyecto.
- **Consecuencias y límite:** La credencial conocida es insegura para entrega/exposición. Debe sustituirse antes de entregar. No existe actualmente una pantalla de cambio de contraseña.

## AUTH-DEC-04 — Clave JWT configurable

- **Estado:** Implementada.
- **Decisión:** Leer `NETOPS_SECRET_KEY`; usar `netops-desk-super-secret-key-local` como fallback de desarrollo.
- **Motivo:** Facilitar la ejecución local sin configuración adicional y permitir configuración externa en despliegues.
- **Consecuencias:** El fallback no sirve para producción. El operador debe proporcionar y custodiar un secreto aleatorio y persistente.

## AUTH-DEC-05 — Token en localStorage y cierre de sesión cliente

- **Estado:** Implementada por instrucción explícita de producto.
- **Decisión:** El frontend guarda `netops_token` en `localStorage`, añade Bearer a llamadas API locales y elimina la sesión ante logout o HTTP 401.
- **Motivo:** Cumplir el flujo web solicitado.
- **Consecuencias:** JavaScript del mismo origen puede leer el token; reducir riesgo XSS y usar HTTPS fuera del entorno local. No existe revocación del token en servidor.
