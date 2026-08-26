from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CategoryRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ExpenseCreate(BaseModel):
    category_id: int
    amount_cents: int = Field(gt=0, description="Сумма в копейках, должна быть положительной")
    spent_at: date
    comment: str = Field(default="", max_length=255, description="Комментарий к расходу")


class ExpenseUpdate(BaseModel):
    category_id: int | None = None
    amount_cents: int | None = Field(default=None, gt=0)
    spent_at: date | None = None
    comment: str | None = Field(default=None, max_length=255)


class ExpenseRead(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount_cents: int
    spent_at: date
    comment: str

    model_config = ConfigDict(from_attributes=True)


class PaginatedExpenses(BaseModel):
    items: list[ExpenseRead]
    total: int
    skip: int
    limit: int


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=150, description="Имя пользователя")
    password: str = Field(min_length=8, max_length=72, description="Пароль")


class UserRead(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MonthlyReportResponse(BaseModel):
    year: int
    month: int
    total_cents: int


class CategoryTotal(BaseModel):
    name: str
    total_cents: int


class ByCategoriesReportResponse(BaseModel):
    year: int
    month: int
    categories: list[CategoryTotal]
