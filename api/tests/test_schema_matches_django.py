from app.models import Category, Expense, User
from sqlalchemy import inspect


def normalize_type(type_str: str) -> str:
    return (
        type_str.upper()
        .replace("DATETIME", "TIMESTAMP")
        .replace("TIMESTAMP WITHOUT TIME ZONE", "TIMESTAMP")
    )


def assert_schema_matches(engine, table_name: str, model) -> None:
    columns = {c["name"]: c for c in inspect(engine).get_columns(table_name)}

    for column in model.__table__.columns:
        assert column.name in columns, f"колонки {column.name} нет в базе"

        db_type = normalize_type(str(columns[column.name]["type"]))
        model_type = normalize_type(str(column.type))
        assert db_type == model_type, f"{column.name}: в базе {db_type}, в модели {model_type}"

        db_nullable = columns[column.name]["nullable"]
        model_nullable = column.nullable
        assert db_nullable == model_nullable, (
            f"{column.name}: в базе nullable={db_nullable}, в модели nullable={model_nullable}"
        )


def test_expense_schema_matches_real_db(engine):
    assert_schema_matches(engine, "core_expense", Expense)


def test_category_schema_matches_real_db(engine):
    assert_schema_matches(engine, "core_category", Category)


def test_user_schema_matches_real_db(engine):
    assert_schema_matches(engine, "auth_user", User)
