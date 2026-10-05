from datetime import datetime, timedelta, timezone

import httpx
import jwt
import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Parking

USER_ID = "00000000-0000-0000-0000-000000000001"
PARKING_WITH_SPACES = "20000000-0000-0000-0000-000000000001"


def token_for(user_id: str, role: str) -> str:
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "development-jwt-secret",
        algorithm="HS256",
    )


def auth_headers(user_id: str = USER_ID, role: str = "USER") -> dict[str, str]:
    return {"Authorization": f"Bearer {token_for(user_id, role)}"}


@pytest.fixture()
def client(monkeypatch):
    def notification_unavailable(*_, **__):
        raise httpx.ConnectError("notification service unavailable")

    monkeypatch.setattr("app.notifications.httpx.post", notification_unavailable)

    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def test_list_vehicles_returns_seed(client: TestClient):
    response = client.get("/vehicles")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_parking_returns_seed(client: TestClient):
    response = client.get("/parking")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_reserve_success_even_if_notification_fails(client: TestClient):
    response = client.post(
        f"/parking/{PARKING_WITH_SPACES}/reserve",
        headers=auth_headers(),
        json={"expires_in_minutes": 30},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["parking_id"] == PARKING_WITH_SPACES
    assert body["user_id"] == USER_ID
    assert body["status"] == "ACTIVE"

    with SessionLocal() as session:
        parking = session.get(Parking, PARKING_WITH_SPACES)
        assert parking.available_spaces == 9


def test_reserve_no_spaces_returns_409(client: TestClient):
    with SessionLocal() as session:
        parking = session.get(Parking, PARKING_WITH_SPACES)
        parking.available_spaces = 0
        session.commit()

    response = client.post(
        f"/parking/{PARKING_WITH_SPACES}/reserve",
        headers=auth_headers(),
        json={"expires_in_minutes": 30},
    )

    assert response.status_code == 409


def test_reserve_requires_jwt(client: TestClient):
    response = client.post(
        f"/parking/{PARKING_WITH_SPACES}/reserve",
        json={"expires_in_minutes": 30},
    )

    assert response.status_code == 401