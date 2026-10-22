"""Rutas para Autenticación."""

from threading import Lock
from time import monotonic

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from netops_desk.api.dependencies import get_current_user
from netops_desk.auth import authenticate_user
from netops_desk.exceptions import DomainError
from netops_desk.repositories.user_repository import SQLiteUserRepository

router = APIRouter(tags=["Auth"])

_LOGIN_WINDOW_SECONDS = 60.0
_LOGIN_BLOCK_SECONDS = 60.0
_LOGIN_MAX_FAILURES = 5
_login_attempts: dict[str, tuple[list[float], float]] = {}
_login_attempts_lock = Lock()


def _is_login_blocked(username: str) -> bool:
    now = monotonic()
    key = username.strip().casefold()
    with _login_attempts_lock:
        entry = _login_attempts.get(key)
        if entry is None:
            return False
        attempts, blocked_until = entry
        if now < blocked_until:
            return True
        if blocked_until:
            _login_attempts.pop(key, None)
            return False
        attempts = [attempt for attempt in attempts if now - attempt < _LOGIN_WINDOW_SECONDS]
        if attempts:
            _login_attempts[key] = (attempts, 0.0)
        else:
            _login_attempts.pop(key, None)
        return False


def _record_login_failure(username: str) -> None:
    now = monotonic()
    key = username.strip().casefold()
    with _login_attempts_lock:
        attempts, blocked_until = _login_attempts.get(key, ([], 0.0))
        if now < blocked_until:
            return
        attempts = [attempt for attempt in attempts if now - attempt < _LOGIN_WINDOW_SECONDS]
        attempts.append(now)
        if len(attempts) >= _LOGIN_MAX_FAILURES:
            _login_attempts[key] = ([], now + _LOGIN_BLOCK_SECONDS)
        else:
            _login_attempts[key] = (attempts, 0.0)


def _clear_login_failures(username: str) -> None:
    with _login_attempts_lock:
        _login_attempts.pop(username.strip().casefold(), None)

def get_user_repo() -> SQLiteUserRepository:
    return SQLiteUserRepository()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/api/v1/auth/login", response_model=TokenResponse)
def login(body: LoginRequest, repo: SQLiteUserRepository = Depends(get_user_repo)):
    if _is_login_blocked(body.username):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "too_many_requests",
                "detail": "Demasiados intentos de inicio de sesión. Reintentá en un minuto.",
            },
        )

    try:
        token = authenticate_user(repo, body.username, body.password)
        _clear_login_failures(body.username)
        return {"access_token": token, "token_type": "bearer"}
    except DomainError as exc:
        if exc.code != "invalid_credentials":
            raise
        _record_login_failure(body.username)
        # Mensaje genérico por seguridad
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials", "detail": "Usuario o contraseña incorrectos."}
        ) from exc

@router.get("/api/v1/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {"username": user["sub"], "role": user["role"]}
