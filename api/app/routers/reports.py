from datetime import date
import calendar

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Category, Expense

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/monthly/")
def monthly_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
):
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    total_cents = db.execute(
        select(func.coalesce(func.sum(Expense.amount_cents), 0)).where(
            Expense.spent_at >= first_day,
            Expense.spent_at <= last_day,
        )
    ).scalar_one()

    return {
        "year": year,
        "month": month,
        "total_cents": total_cents,
    }


@router.get("/by-categories/")
def by_categories_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
):
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    rows = db.execute(
        select(
            Category.name,
            func.coalesce(func.sum(Expense.amount_cents), 0),
        )
        .outerjoin(Expense, Category.id == Expense.category_id)
        .where(
            Expense.spent_at >= first_day,
            Expense.spent_at <= last_day,
        )
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Expense.amount_cents).desc())
    ).all()

    return {
        "year": year,
        "month": month,
        "categories": [
            {"name": name, "total_cents": total}
            for name, total in rows
        ],
    }