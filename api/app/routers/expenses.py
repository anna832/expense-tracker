from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Category, Expense
from app.schemas import (
    ExpenseCreate,
    ExpenseRead,
    ExpenseUpdate,
    PaginatedExpenses,
)

router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])

DbSession = Annotated[Session, Depends(get_db)]

SkipParam = Annotated[int, Query(ge=0, description="Сколько записей пропустить")]
LimitParam = Annotated[int, Query(ge=1, le=100, description="Сколько записей вернуть")]
CategoryFilterParam = Annotated[int | None, Query(description="Фильтр по категории")]
DateFromParam = Annotated[date | None, Query(description="Фильтр: не раньше даты")]
DateToParam = Annotated[date | None, Query(description="Фильтр: не позже даты")]


@router.post("/", response_model=ExpenseRead, status_code=201)
def create_expense(data: ExpenseCreate, db: DbSession):
    category = db.get(Category, data.category_id)
    if category is None:
        raise HTTPException(status_code=400, detail="Category not found")

    expense = Expense(
        category_id=data.category_id,
        amount_cents=data.amount_cents,
        spent_at=data.spent_at,
        comment=data.comment,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/", response_model=PaginatedExpenses)
def list_expenses(
    db: DbSession,
    skip: SkipParam = 0,
    limit: LimitParam = 50,
    category_id: CategoryFilterParam = None,
    date_from: DateFromParam = None,
    date_to: DateToParam = None,
):
    conditions = []
    if category_id is not None:
        conditions.append(Expense.category_id == category_id)
    if date_from is not None:
        conditions.append(Expense.spent_at >= date_from)
    if date_to is not None:
        conditions.append(Expense.spent_at <= date_to)

    base_query = select(Expense)
    if conditions:
        base_query = base_query.where(and_(*conditions))

    total = db.execute(select(func.count()).select_from(base_query.subquery())).scalar_one()

    expenses = (
        db.execute(
            base_query.order_by(Expense.spent_at.desc(), Expense.id.desc())
            .offset(skip)
            .limit(limit)
        )
        .scalars()
        .all()
    )

    return PaginatedExpenses(
        items=expenses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{expense_id}/", response_model=ExpenseRead)
def get_expense(expense_id: int, db: DbSession):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.patch("/{expense_id}/", response_model=ExpenseRead)
def update_expense(expense_id: int, data: ExpenseUpdate, db: DbSession):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}/", status_code=204)
def delete_expense(expense_id: int, db: DbSession):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()
    return None
