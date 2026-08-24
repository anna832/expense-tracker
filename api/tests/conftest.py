import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import pytest
from app.db import get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

DJANGO_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent / "django_admin"


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def database_url(postgres_container):
    url = postgres_container.get_connection_url()
    url = url.replace("postgresql+psycopg2", "postgresql+psycopg")
    return url


@pytest.fixture(scope="session", autouse=True)
def apply_django_migrations(database_url, postgres_container):
    parsed = urlparse(postgres_container.get_connection_url())

    env = os.environ.copy()
    env["POSTGRES_HOST"] = parsed.hostname
    env["POSTGRES_PORT"] = str(parsed.port)
    env["POSTGRES_DB"] = parsed.path.lstrip("/")
    env["POSTGRES_USER"] = parsed.username
    env["POSTGRES_PASSWORD"] = parsed.password

    subprocess.run(
        [sys.executable, "manage.py", "migrate", "--noinput"],
        cwd=DJANGO_PROJECT_DIR,
        env=env,
        check=True,
    )


@pytest.fixture(scope="session")
def engine(database_url):
    return create_engine(database_url)


@pytest.fixture()
def db_session(engine):
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_tables(db_session):
    yield
    from app.models import Base

    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
