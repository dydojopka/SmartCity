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


def test_create_notification_success(client: TestClient, monkeypatch):
    monkeypatch.setenv("SERVICE_TOKEN", "test-service-token")

    response = client.post(
        "/notifications",
        headers={"X-Service-Token": "test-service-token"},
        json={
            "user_id": "00000000-0000-0000-0000-000000000001",
            "recipient": "user@example.com",
            "channel": "EMAIL",
            "subject": "Тест",
            "message": "Проверка уведомления",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SENT"
    assert data["sent_at"] is not None
    assert "token" not in str(data).lower()


def test_create_notification_invalid_token(client: TestClient, monkeypatch):
    monkeypatch.setenv("SERVICE_TOKEN", "test-service-token")

    response = client.post(
        "/notifications",
        headers={"X-Service-Token": "wrong-token"},
        json={
            "recipient": "user@example.com",
            "channel": "EMAIL",
            "message": "Проверка уведомления",
        },
    )

    assert response.status_code == 401