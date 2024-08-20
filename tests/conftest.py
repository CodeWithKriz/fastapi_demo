from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import pytest

from app.config import settings
from app.database import get_db, Base
from app.main import app
from app import oauth2
from app import models, schemas

engine = create_engine(
    settings.test_db_url, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def create_user(client):
    def _method(new_user_data):
        resp = client.post("/api/v1/users", data=new_user_data)
        assert resp.status_code == status.HTTP_201_CREATED
        new_user = schemas.GetUser(**resp.json())
        return new_user
    return _method

@pytest.fixture(scope="function")
def login_user(client, session):
    def _method(login_data):
        resp = client.post("/api/v1/auth", data=login_data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json.get("token_type") == "bearer"
        assert resp_json.get("access_token") is not None
        current_user =  oauth2.get_current_user(token=resp_json.get("access_token"), db=session)
        assert ((login_data["username"] == current_user.username) or ((login_data["username"] == current_user.email)))
        return resp_json.get("access_token")
    return _method
