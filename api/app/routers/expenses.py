from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Category, Expense
from app.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])


def get_expense_or_404(expense_id: int, db: Session) -> Expense:
    expense: Expense | None = db.get(Expense, expense_id)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return expense


def check_category_exists(category_id: int, db: Session) -> None:
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category does not exist",
        )


@router.post("/", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    check_category_exists(payload.category_id, db)

    expense = Expense(
        category_id=payload.category_id,
        amount_cents=payload.amount_cents,
        spent_at=payload.spent_at,
        comment=payload.comment,
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


@router.get("/", response_model=list[ExpenseRead])
def list_expenses(db: Session = Depends(get_db)):
    expenses = db.execute(
        select(Expense).order_by(Expense.spent_at.desc(), Expense.id.desc())
    ).scalars().all()
    return expenses


@router.get("/{expense_id}/", response_model=ExpenseRead)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    return get_expense_or_404(expense_id, db)


@router.patch("/{expense_id}/", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
):
    expense = get_expense_or_404(expense_id, db)

    if payload.category_id is not None:
        check_category_exists(payload.category_id, db)
        expense.category_id = payload.category_id

    if payload.amount_cents is not None:
        expense.amount_cents = payload.amount_cents

    if payload.spent_at is not None:
        expense.spent_at = payload.spent_at

    if payload.comment is not None:
        expense.comment = payload.comment

    db.commit()
    db.refresh(expense)

    return expense


@router.delete("/{expense_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = get_expense_or_404(expense_id, db)

    db.delete(expense)
    db.commit()