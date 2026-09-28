from datetime import datetime, timedelta, timezone

import jwt
import pytest
import httpx
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

USER_ID = "00000000-0000-0000-0000-000000000001"
OPERATOR_ID = "00000000-0000-0000-0000-000000000002"


def token_for(user_id: str, role: str) -> str:
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "development-jwt-secret",
        algorithm="HS256",
    )


def auth_headers(user_id: str, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_for(user_id, role)}"}


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def test_user_creates_and_sees_own_issue(client: TestClient):
    response = client.post(
        "/issues",
        headers=auth_headers(USER_ID, "USER"),
        json={
            "title": "Не работает светофор",
            "description": "На перекрёстке не включается зелёный свет",
            "category": "TRAFFIC",
            "address": "Литейный проспект, 5",
        },
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == USER_ID
    issues = client.get("/issues", headers=auth_headers(USER_ID, "USER"))
    assert issues.status_code == 200
    assert all(issue["user_id"] == USER_ID for issue in issues.json())


def test_user_cannot_change_status(client: TestClient):
    issue_id = "90000000-0000-0000-0000-000000000001"
    response = client.put(
        f"/issues/{issue_id}",
        headers=auth_headers(USER_ID, "USER"),
        json={"status": "IN_PROGRESS"},
    )

    assert response.status_code == 403


def test_operator_changes_status_even_if_notification_fails(client: TestClient, monkeypatch):
    def notification_unavailable(*_, **__):
        raise httpx.ConnectError("notification service unavailable")

    monkeypatch.setattr("app.notifications.httpx.post", notification_unavailable)
    issue_id = "90000000-0000-0000-0000-000000000001"

    response = client.put(
        f"/issues/{issue_id}",
        headers=auth_headers(OPERATOR_ID, "OPERATOR"),
        json={"status": "IN_PROGRESS"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"
