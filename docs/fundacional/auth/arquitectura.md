# Arquitectura — Autenticación y login

> Estado: describe la implementación presente según inspección del repositorio.

## Componentes

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| Dominio de autenticación | `src/netops_desk/auth.py` | Verificar credenciales, emitir y validar JWT. Usa PyJWT y `pwdlib`. |
| Repositorio | `src/netops_desk/repositories/user_repository.py` | Crear/consultar usuarios y tabla SQLite `users`; aprovisionar el usuario inicial. |
| Dependencia de identidad | `src/netops_desk/api/dependencies.py` | Extraer y validar Bearer token, proporcionar usuario autenticado. |
| API | `src/netops_desk/api/routes/auth.py`, `src/netops_desk/api/main.py` | Login público, `/me` protegido y protección de routers de herramientas. |
| Errores HTTP | `src/netops_desk/api/exceptions.py` | Convertir excepciones a sobre `{error, detail}`, preservando el código de error 401. |
| Login web | `static/login.html`, `static/js/login.js` | Enviar credenciales al endpoint real, guardar token y mostrar errores. |
| Sesión compartida | `static/js/common.js` | Añadir Bearer a llamadas API locales, responder ante 401 y cerrar sesión. |
| Dashboard | `static/js/dashboard.js`, `static/js/sidebar.js` | Consultar `/me`, presentar identidad y ofrecer logout. |

## Flujo

1. `login.js` envía username y password a `POST /api/v1/auth/login`.
2. La API ejecuta el endpoint de login como función síncrona; FastAPI realiza la verificación Argon2 de `pwdlib` en su threadpool y consulta el repositorio SQLite.
3. Ante éxito, `auth.py` firma un JWT HS256 con `sub`, `role` y `exp` de ocho horas.
4. El navegador guarda `access_token` bajo `netops_token` en `localStorage` y navega a `/`.
5. `common.js` adjunta el Bearer a llamadas del mismo origen bajo `/api/`, excepto al login. Ante 401 borra token y usuario y redirige a `/login`.
6. El dashboard llama `/api/v1/auth/me` y presenta username y role. El cierre de sesión solo elimina credenciales del navegador.

## Datos y configuración

SQLite mantiene `users` con username único, `password_hash` y `role` además de su identificador. El repositorio inicializa la base y crea `admin`/`admin` cuando no hay usuarios. La clave de firma se obtiene de `NETOPS_SECRET_KEY` o, si falta, usa la clave local de desarrollo definida en `auth.py`. Los tokens emitidos con una clave anterior dejan de ser válidos cuando la configuración cambia.

## Límites de seguridad

- No hay ejecución de comandos ni acceso al sistema operativo como parte de autenticación.
- Login queda fuera de la dependencia global; las rutas de herramientas y `/me` siguen protegidas.
- Los roles se incorporan al token y se exponen al cliente, pero la presencia del rol no constituye una matriz de permisos por operación.
- No hay endpoint de logout del servidor, refresh token, lista de revocación ni cambio de contraseña.
- El token en `localStorage` puede leerse desde JavaScript del origen. Mantener dependencias del frontend controladas, evitar XSS y usar HTTPS en despliegues.
- `admin`/`admin` y la clave local conocida son solo para desarrollo/demo; antes de entrega a cliente se requiere rotar la contraseña y configurar una clave secreta externa. La aplicación no dispone todavía de flujo de cambio de contraseña.
