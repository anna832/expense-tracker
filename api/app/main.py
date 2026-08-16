from fastapi import FastAPI

from app.routers import categories, expenses, reports

app = FastAPI(
    title="Expense Tracker API",
    version="0.1.0",
)

app.include_router(categories.router)
app.include_router(expenses.router)
app.include_router(reports.router)

@app.get("/api/v1/health/")
def health():
    return {
        "status": "ok",
    }