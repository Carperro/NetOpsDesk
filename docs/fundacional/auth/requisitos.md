# Requisitos — Autenticación y login

> Estado: implementado en backend e interfaz. La verificación de esta entrega se informa por separado.

## Propósito y alcance

Autenticar usuarios locales contra SQLite, proteger las API de herramientas y permitir iniciar y cerrar sesión desde la interfaz. El sistema usa JWT Bearer y los roles `admin` y `user`. No incluye registro público, recuperación o cambio de contraseña, autorización diferenciada por herramienta ni revocación de tokens en servidor.

## Requisitos funcionales

| ID | Requisito | Comportamiento actual |
|---|---|---|
| AUTH-F-001 | Mantener usuarios en SQLite | Tabla `users` con ID, username único, hash de contraseña y rol. |
| AUTH-F-002 | Aprovisionar administrador inicial | El repositorio crea `admin`/`admin` cuando inicializa una base sin usuarios. Credencial solo para entorno local/demo; debe cambiarse antes de entregar. |
| AUTH-F-003 | Iniciar sesión | `POST /api/v1/auth/login` valida credenciales y devuelve un token JWT. La ruta es pública. |
| AUTH-F-004 | Proteger las herramientas | Las rutas `/api/v1/tools/*` requieren un Bearer JWT válido. |
| AUTH-F-005 | Consultar identidad | `GET /api/v1/auth/me` requiere token y devuelve `username` y `role`. |
| AUTH-F-006 | Iniciar sesión desde navegador | `login.html` y `login.js` envían credenciales; el token se guarda en `localStorage` y se redirige al inicio. |
| AUTH-F-007 | Cerrar sesión | La interfaz borra el token y los datos de usuario locales, y redirige a `/login`. No invalida tokens en el servidor. |

## Requisitos no funcionales

- Las contraseñas se guardan con `pwdlib` y Argon2; nunca en texto plano.
- JWT firmado con HS256, con expiración de ocho horas. `NETOPS_SECRET_KEY` configura la clave; el valor incluido por defecto es únicamente para desarrollo local.
- Las peticiones API locales incluyen `Authorization: Bearer <token>`. Una respuesta 401 elimina la sesión local y redirige a `/login`.
- Credenciales inválidas devuelven HTTP 401 con código `invalid_credentials` y mensaje genérico.
- Web Storage es accesible para JavaScript del mismo origen; proteger el frontend contra XSS y usar HTTPS fuera de uso estrictamente local.

## Criterios de aceptación

- Credenciales correctas producen HTTP 200 con `access_token` y `token_type`.
- Credenciales incorrectas producen HTTP 401 y `error: invalid_credentials`.
- `/api/v1/auth/login` es accesible sin token; `/api/v1/auth/me` y las rutas de herramientas requieren autenticación.
- El navegador envía el token a la API, muestra el usuario de `/me`, y al cerrar sesión o recibir 401 limpia la sesión local.
- Ninguna contraseña ni token se presenta como HTML interpretado o se registra intencionalmente.
