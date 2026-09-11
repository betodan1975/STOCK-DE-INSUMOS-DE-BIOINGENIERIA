"""Autenticacion: bcrypt + JWT (opcional).

AUTH_DISABLED=1 (default)  -> los endpoints quedan abiertos. get_current_user()
                              devuelve un usuario virtual "local" con rol admin.
AUTH_DISABLED=0            -> auth obligatoria con JWT (el comportamiento "viejo").

Variables relevantes:
    AUTH_DISABLED     -- "1" deshabilita la verificacion (default).
    JWT_SECRET        -- secret para firmar JWT (solo se usa si AUTH_DISABLED=0).
    JWT_EXPIRE_HOURS  -- horas de vida del token (default 12).
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import models
from database import get_db

log = logging.getLogger("auth")

_DEFAULT_SECRET = "stock-insumos-dev-secret-CAMBIAR-EN-PRODUCCION"
JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    JWT_SECRET = _DEFAULT_SECRET

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.environ.get("JWT_EXPIRE_HOURS", "12"))

# Login activo por default. Para volver a modo "sin login" (uso local en una
# sola maquina, todos entran como admin virtual): setear AUTH_DISABLED=1 en el
# entorno antes de levantar uvicorn.
AUTH_DISABLED = os.environ.get("AUTH_DISABLED", "0") not in ("0", "false", "False", "")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# Usamos la libreria `bcrypt` directamente (en vez de passlib.CryptContext).
# passlib 1.7.x detecta la version de bcrypt leyendo `bcrypt.__about__`, que
# las versiones de bcrypt >=4.1 eliminaron -> esto rompe pwd_context.hash()
# con un 500 al crear/editar usuarios. Llamando a bcrypt.hashpw/checkpw
# directamente evitamos ese problema de compatibilidad por completo.
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(*, sub: str, extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXPIRE_HOURS)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def _default_local_user() -> models.Usuario:
    """Usuario virtual usado cuando AUTH_DISABLED=1. No se persiste en DB."""
    u = models.Usuario(
        id=0,
        username="local",
        password_hash="",
        nombre="Operador local",
        rol="admin",
        activo=True,
    )
    return u


_credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> models.Usuario:
    if AUTH_DISABLED:
        # Si igual viene un token valido, lo respetamos (asi /auth/me devuelve
        # el usuario real); sino devolvemos el "local" virtual.
        if token:
            try:
                payload = decode_access_token(token)
                username = payload.get("sub")
                if username:
                    user = db.query(models.Usuario).filter_by(username=username).first()
                    if user and user.activo:
                        return user
            except JWTError:
                pass
        return _default_local_user()

    # AUTH habilitada (modo viejo).
    if not token:
        raise _credentials_exc
    try:
        payload = decode_access_token(token)
        username: str | None = payload.get("sub")
        if not username:
            raise _credentials_exc
    except JWTError:
        raise _credentials_exc
    user = db.query(models.Usuario).filter_by(username=username).first()
    if not user or not user.activo:
        raise _credentials_exc
    return user


def require_admin(user: Annotated[models.Usuario, Depends(get_current_user)]) -> models.Usuario:
    if AUTH_DISABLED:
        return user  # local siempre es admin
    if user.rol != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol admin")
    return user
