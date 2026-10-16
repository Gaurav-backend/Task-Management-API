import os
from dotenv import dotenv_values

test_env = dotenv_values(".env")

os.environ.setdefault(
    "DATABASE_URL",
    test_env.get("DATABASE_URL") or "sqlite:///./test_bootstrap.db",
)
os.environ.setdefault(
    "SECRET_KEY",
    test_env.get("SECRET_KEY") or "test-only-secret-key",
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
import pytest

from app.database.database import Base, get_db
from app.main import app
from app.models.task import Task
from app.core.security import get_current_active_user
from app.models.user import User

class TestSettings(BaseSettings):
    TEST_DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
        )


test_settings = TestSettings()

test_engine = create_engine(
    test_settings.TEST_DATABASE_URL
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

@pytest.fixture
def setup_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(setup_database):
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def second_db_session(setup_database):
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    # Create a real user in the test database so the
    # task's owner_id foreign key points to an existing user.
    test_user = User(
        id=1,
        email="test@example.com",
        username="testuser",
        password_hash=None,
        is_active=True,
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    def override_get_db():
        yield db_session

    def override_get_current_active_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[
        get_current_active_user
    ] = override_get_current_active_user

    from fastapi.testclient import TestClient

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()