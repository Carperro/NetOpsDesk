# NetOps Desk

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Versión:** 0.1.0 · **Python:** 3.12+ · **Licencia:** MIT

NetOps Desk es una aplicación web local para herramientas de redes y soporte IT. El catálogo del MVP contiene 25 herramientas distribuidas en cinco módulos. La aplicación incluye autenticación JWT, una interfaz servida por FastAPI y almacenamiento SQLite local.

## Instalación para usuarios

Se requiere Python 3.12 o superior. Desde la raíz del repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m uvicorn netops_desk.api.main:app --host 127.0.0.1 --port 8000
```

Abrí <http://127.0.0.1:8000>. La aplicación crea `netops.db` automáticamente cuando inicializa el repositorio de usuarios. La cuenta local inicial es `admin` con contraseña `admin`; cambiá esas credenciales antes de entregar o exponer la aplicación. No hay una pantalla de cambio de contraseña incluida actualmente. En desarrollo, podés borrar `netops.db` para volver a crear la cuenta inicial (esto elimina los datos guardados). En producción, respaldá la base y actualizá `users.password_hash` con un hash generado por `pwdlib`; nunca guardes la contraseña en texto plano.

La base `netops.db` se crea en el directorio de trabajo actual (`cwd`) desde el que se inicia Uvicorn. Usá siempre el mismo directorio de trabajo para que la aplicación encuentre la misma base.

### Autenticación de la API

El endpoint de login es público. Las rutas de herramientas requieren un JWT en `Authorization: Bearer <token>`. En PowerShell, primero solicitá el token:

```powershell
$login = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
  -ContentType "application/json" `
  -Body (@{ username = "admin"; password = "admin" } | ConvertTo-Json)
$token = $login.access_token
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/me" `
  -Headers @{ Authorization = "Bearer $token" }
```

En cURL/Bash:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' | python -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
```

En Postman, enviá `POST /api/v1/auth/login` con `Content-Type: application/json` y el cuerpo `{"username":"admin","password":"admin"}`; copiá `access_token` de la respuesta. Para `/api/v1/auth/me` o una ruta de herramientas, configurá Authorization como Bearer Token o agregá el header manualmente. En cURL:

```bash
curl http://127.0.0.1:8000/api/v1/auth/me -H "Authorization: Bearer $TOKEN"
```

La respuesta del login tiene la forma `{"access_token":"<jwt>","token_type":"bearer"}`. Las credenciales iniciales son solo para desarrollo/demo y deben cambiarse antes de entregar la aplicación.

### Clave JWT

La aplicación usa una clave JWT por defecto para desarrollo local. En producción, es **OBLIGATORIO** definir `NETOPS_SECRET_KEY` con un secreto aleatorio, privado y persistente antes de iniciar Uvicorn. Si no se configura otra clave, actualmente se usa `netops-desk-super-secret-key-local`. Por ejemplo, en PowerShell para la sesión actual:

```powershell
$env:NETOPS_SECRET_KEY = "reemplazar-por-un-secreto-aleatorio-largo"
python -m uvicorn netops_desk.api.main:app --host 127.0.0.1 --port 8000
```

Guardá el secreto real en el gestor de secretos del entorno; no lo agregues al repositorio. Si cambia la clave, los tokens emitidos con la anterior dejan de validarse.

## Desarrollo y pruebas

```powershell
python -m pip install -e ".[test,dev]"
python -m pytest tests/ -q
```

La guía de dependencias bloqueadas para desarrollo está en `requirements.lock`; para una instalación de usuario se puede instalar el proyecto directamente con `pip install -e .`.

### Auditoría de dependencias

En PowerShell, ejecutá `./scripts/audit.ps1`. El script usa `pip-audit` si está instalado y, en caso contrario, ejecuta `pip check` para detectar dependencias incompatibles o faltantes. `pip check` no reemplaza el análisis de vulnerabilidades de `pip-audit`.
