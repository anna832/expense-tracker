from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ExpenseCreate(BaseModel):
    category_id: int
    amount_cents: int = Field(gt=0)
    spent_at: date
    comment: str = ""


class ExpenseUpdate(BaseModel):
    category_id: int | None = None
    amount_cents: int | None = Field(default=None, gt=0)
    spent_at: date | None = None
    comment: str | None = None


class ExpenseRead(BaseModel):
    id: int
    category_id: int
    amount_cents: int
    spent_at: date
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedExpenses(BaseModel):
    items: list[ExpenseRead]
    total: int
    skip: int
    limit: int
