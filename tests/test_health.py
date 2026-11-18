from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.adapters.api.app import create_app
from app.adapters.api.dependencies import get_session


class BrokenSession:
    """Stands in for a session whose database is down."""

    def execute(self, *args: object, **kwargs: object) -> None:
        raise OperationalError("SELECT 1", {}, Exception("database is down"))


@pytest.fixture
def app() -> Iterator[FastAPI]:
    engine = create_engine(
        "sqlite+pysqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    yield create_app(sessionmaker(bind=engine))
    engine.dispose()


def test_health_is_ok_when_the_database_answers(app: FastAPI) -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_is_unavailable_when_the_database_is_down(app: FastAPI) -> None:
    app.dependency_overrides[get_session] = lambda: BrokenSession()

    response = TestClient(app).get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
