from datetime import datetime, timedelta, timezone

import httpx
import jwt
import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Invoice, Payment
from app.seed import USER_ANNA, USER_IVAN, USER_PAVEL

INVOICE_IVAN_UNPAID = "50000000-0000-0000-0000-000000000001"
SERVICE_TOKEN = "development-service-token"


def token_for(user_id: str, role: str) -> str:
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "development-jwt-secret",
        algorithm="HS256",
    )


def auth_headers(user_id: str = USER_IVAN, role: str = "USER") -> dict[str, str]:
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


def test_user_sees_own_invoices(client: TestClient):
    response = client.get(
        f"/accounts/{USER_IVAN}/invoices", headers=auth_headers(USER_IVAN, "USER")
    )

    assert response.status_code == 200
    assert all(inv["user_id"] == USER_IVAN for inv in response.json())
    assert len(response.json()) == 2


def test_user_cannot_see_foreign_invoices(client: TestClient):
    response = client.get(
        f"/accounts/{USER_ANNA}/invoices", headers=auth_headers(USER_IVAN, "USER")
    )

    assert response.status_code == 403


def test_admin_sees_foreign_invoices(client: TestClient):
    response = client.get(
        f"/accounts/{USER_IVAN}/invoices", headers=auth_headers(USER_PAVEL, "ADMIN")
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_repeated_idempotency_key_returns_same_payment(client: TestClient):
    body = {"invoice_id": INVOICE_IVAN_UNPAID, "idempotency_key": "idem-key-1"}

    first = client.post("/payments", headers=auth_headers(), json=body)
    second = client.post("/payments", headers=auth_headers(), json=body)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]

    with SessionLocal() as session:
        assert session.query(Payment).count() == 1


def test_payment_requires_own_invoice(client: TestClient):
    body = {"invoice_id": "50000000-0000-0000-0000-000000000003", "idempotency_key": "idem-key-x"}

    response = client.post("/payments", headers=auth_headers(USER_IVAN, "USER"), json=body)

    assert response.status_code == 403


def test_repeated_webhook_is_idempotent(client: TestClient):
    create = client.post(
        "/payments",
        headers=auth_headers(),
        json={"invoice_id": INVOICE_IVAN_UNPAID, "idempotency_key": "idem-webhook-1"},
    )
    payment_id = create.json()["id"]

    webhook_body = {"external_event_id": "ext-event-1", "payment_id": payment_id}
    headers = {"X-Service-Token": SERVICE_TOKEN}

    first = client.post("/payments/webhook/success", json=webhook_body, headers=headers)
    second = client.post("/payments/webhook/success", json=webhook_body, headers=headers)

    assert first.status_code == 200
    assert first.json()["status"] == "success"
    assert second.status_code == 200
    assert second.json()["status"] == "already_processed"

    with SessionLocal() as session:
        invoice = session.get(Invoice, INVOICE_IVAN_UNPAID)
        assert invoice.status == "PAID"


def test_webhook_rejects_invalid_token(client: TestClient):
    response = client.post(
        "/payments/webhook/success",
        json={"external_event_id": "ext-event-x", "payment_id": "whatever"},
        headers={"X-Service-Token": "wrong-token"},
    )

    assert response.status_code == 401