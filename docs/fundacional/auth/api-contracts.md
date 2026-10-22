# Contrato de API — Autenticación y login

> Estado: refleja rutas y respuestas implementadas.

## Iniciar sesión

- **Método/ruta:** `POST /api/v1/auth/login`
- **Autenticación:** no requerida.
- **Content-Type:** `application/json`.

Solicitud:

```json
{
  "username": "admin",
  "password": "admin"
}
```

Respuesta `200 OK`:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

Error de credenciales `401 Unauthorized`:

```json
{
  "error": "invalid_credentials",
  "detail": "Usuario o contraseña incorrectos."
}
```

El cuerpo debe incluir username y password como cadenas. Los errores de forma del request siguen el sobre de validación común de la API.

## Consultar identidad

- **Método/ruta:** `GET /api/v1/auth/me`
- **Autenticación:** requerida.
- **Header:** `Authorization: Bearer <token>`.

Respuesta `200 OK`:

```json
{
  "username": "admin",
  "role": "admin"
}
```

Token ausente o no aceptado produce HTTP 401. El cuerpo preserva el código de autenticación que proporciona la dependencia, por ejemplo `unauthorized`, `invalid_token` o `token_expired`.

## Protección de herramientas

Todas las rutas registradas bajo `/api/v1/tools/*` requieren el mismo header Bearer. El endpoint de login permanece público para permitir obtener el token. La autenticación es por usuario; este contrato no asigna permisos diferenciados por rol.

## Sesión del navegador

El cliente almacena el token en `localStorage` bajo `netops_token` y lo agrega a solicitudes API locales. Al recibir 401, limpia token y usuario y navega a `/login`. Logout es exclusivamente local; no hay endpoint de revocación o cierre de sesión del servidor. La validez máxima del JWT es de ocho horas.
