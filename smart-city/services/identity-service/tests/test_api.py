from fastapi.testclient import TestClient
import pytest

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def test_register_and_duplicate_email(client: TestClient):
    payload = {
        "email": "new.user@example.com",
        "password": "safe-password-123",
        "first_name": "Новый",
        "last_name": "Пользователь",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]
    assert "password_hash" not in response.json()
    assert "password" not in response.json()
    assert client.post("/auth/register", json=payload).status_code == 409


def test_login_and_current_user(client: TestClient):
    login_response = client.post(
        "/auth/login",
        json={"email": "user@smartcity.local", "password": "demo12345"},
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    profile_response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert profile_response.status_code == 200
    assert profile_response.json()["id"] == "00000000-0000-0000-0000-000000000001"


def test_login_rejects_wrong_password(client: TestClient):
    response = client.post(
        "/auth/login",
        json={"email": "user@smartcity.local", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_current_user_requires_jwt(client: TestClient):
    assert client.get("/users/me").status_code == 401
