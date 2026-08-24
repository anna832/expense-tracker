from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Category, Expense
from app.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])

DbSession = Annotated[Session, Depends(get_db)]


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


@router.get("/", response_model=list[ExpenseRead])
def list_expenses(db: DbSession):
    expenses = db.execute(select(Expense).order_by(Expense.spent_at.desc())).scalars().all()
    return expenses


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
