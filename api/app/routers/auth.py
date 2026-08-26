from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.db import get_db
from app.models import User
from app.schemas import TokenResponse, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/register/", response_model=UserRead, status_code=201)
def register(data: UserCreate, db: DbSession):
    existing = db.execute(select(User).where(User.username == data.username)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=data.username,
        password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login/", response_model=TokenResponse)
def login(data: UserLogin, db: DbSession):
    user = db.execute(select(User).where(User.username == data.username)).scalar_one_or_none()
    if user is None or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me/", response_model=UserRead)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
