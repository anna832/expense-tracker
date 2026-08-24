from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Category
from app.schemas import CategoryRead

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[CategoryRead])
def list_categories(db: DbSession):
    categories = db.execute(select(Category).order_by(Category.name)).scalars().all()
    return categories
