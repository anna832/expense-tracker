from datetime import date
import calendar

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, and_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Category, Expense

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

def get_month_range(year: int, month: int) -> tuple[date, date]:
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day

@router.get("/monthly/")
def monthly_report(
        year: int = Query(..., ge=2000, le=2100, description="Год отчёта"),
        month: int = Query(..., ge=1, le=12, description="Месяц отчёта"),
        db: Session = Depends(get_db),
):
    first_day, last_day = get_month_range(year, month)

    total_cents = db.execute(
        select(func.coalesce(func.sum(Expense.amount_cents), 0)).where(
            and_(
                Expense.spent_at >= first_day,
                Expense.spent_at <= last_day,
            )
        )
    ).scalar_one()

    return {
        "year": year,
        "month": month,
        "total_cents": total_cents,
    }


@router.get("/by-categories/")
def by_categories_report(
        year: int = Query(..., ge=2000, le=2100, description="Год отчёта"),
        month: int = Query(..., ge=1, le=12, description="Месяц отчёта"),
        db: Session = Depends(get_db),
):
    first_day, last_day = get_month_range(year, month)

    rows = db.execute(
        select(
            Category.name,
            func.coalesce(func.sum(Expense.amount_cents), 0),
        )
        .outerjoin(Expense,
                   and_(
                        Category.id == Expense.category_id,
                        Expense.spent_at >= first_day,
                        Expense.spent_at <= last_day,
                   ))
        .group_by(Category.id, Category.name)
        .order_by(func.coalesce(func.sum(Expense.amount_cents), 0).desc())
    ).all()

    return {
        "year": year,
        "month": month,
        "categories": [
            {"name": name, "total_cents": total}
            for name, total in rows
        ],
    }