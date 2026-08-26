import binascii
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import User

security = HTTPBearer()

CredentialsDep = Annotated[HTTPAuthorizationCredentials, Depends(security)]
DbSession = Annotated[Session, Depends(get_db)]


def hash_password(password: str) -> str:
    digest = binascii.hexlify(hashlib.sha256(password.encode()).digest())
    return "bcrypt_sha256$" + bcrypt.hashpw(digest, bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password.startswith("bcrypt_sha256$"):
        return False
    digest = binascii.hexlify(hashlib.sha256(plain_password.encode()).digest())
    return bcrypt.checkpw(digest, hashed_password.split("$", 1)[1].encode())


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from None


def get_current_user(
    credentials: CredentialsDep,
    db: DbSession,
) -> User:
    user_id = decode_access_token(credentials.credentials)
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
