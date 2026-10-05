import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_database

SERVICE_NAME = os.getenv("SERVICE_NAME", "billing-service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    logger.info("%s started", SERVICE_NAME)
    yield


app = FastAPI(title="Billing Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}
import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db, init_database
from app.models import Invoice, Payment, WebhookEvent
from app.notifications import notify_payment_success
from app.schemas import (
    InvoiceResponse,
    PaymentCreateRequest,
    PaymentResponse,
    PaymentWebhookRequest,
    PaymentWebhookResponse,
)
from app.seed import seed_database

SERVICE_NAME = os.getenv("SERVICE_NAME", "billing-service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)

SERVICE_TOKEN = os.getenv("SERVICE_TOKEN", "development-service-token")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    from app.database import SessionLocal

    with SessionLocal() as session:
        seed_database(session)
    logger.info("%s started", SERVICE_NAME)
    yield


app = FastAPI(title="Billing Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/accounts/{user_id}/invoices", response_model=list[InvoiceResponse])
def list_user_invoices(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Invoice]:
    if current_user.id != user_id and current_user.role != "ADMIN":
        logger.warning(
            "invoices_access_denied requested_user_id=%s current_user_id=%s",
            user_id,
            current_user.id,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")

    return list(
        db.scalars(
            select(Invoice)
            .where(Invoice.user_id == user_id)
            .order_by(Invoice.created_at.desc())
        ).all()
    )


@app.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Payment:
    existing = db.scalar(
        select(Payment).where(Payment.idempotency_key == payload.idempotency_key)
    )
    if existing is not None:
        logger.info("payment_idempotent_hit idempotency_key=%s", payload.idempotency_key)
        return existing

    invoice = db.get(Invoice, payload.invoice_id)
    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Счёт не найден")

    if invoice.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")

    if invoice.status != "UNPAID":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Счёт не ожидает оплаты"
        )

    payment = Payment(
        id=str(uuid4()),
        invoice_id=invoice.id,
        user_id=current_user.id,
        amount_cents=invoice.amount_cents,
        status="PENDING",
        idempotency_key=payload.idempotency_key,
    )
    db.add(payment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(
            select(Payment).where(Payment.idempotency_key == payload.idempotency_key)
        )
        if existing is not None:
            return existing
        raise

    db.refresh(payment)
    logger.info(
        "payment_created payment_id=%s invoice_id=%s user_id=%s amount_cents=%s",
        payment.id,
        invoice.id,
        current_user.id,
        payment.amount_cents,
    )
    return payment


@app.post("/payments/webhook/success", response_model=PaymentWebhookResponse)
def payment_webhook_success(
    payload: PaymentWebhookRequest,
    db: Annotated[Session, Depends(get_db)],
    x_service_token: Annotated[str, Header(alias="X-Service-Token")],
) -> PaymentWebhookResponse:
    if x_service_token != SERVICE_TOKEN:
        logger.warning("webhook_invalid_service_token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный служебный токен")

    existing_event = db.scalar(
        select(WebhookEvent).where(WebhookEvent.external_event_id == payload.external_event_id)
    )
    if existing_event is not None:
        logger.info(
            "webhook_already_processed external_event_id=%s", payload.external_event_id
        )
        return PaymentWebhookResponse(status="already_processed")

    payment = db.get(Payment, payload.payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Платёж не найден")

    if payment.status == "SUCCESS":
        db.add(
            WebhookEvent(
                id=str(uuid4()),
                external_event_id=payload.external_event_id,
                event_type="PAYMENT_SUCCESS",
                payload=payload.model_dump(),
            )
        )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
        return PaymentWebhookResponse(status="already_processed", payment_id=payment.id)

    invoice = db.get(Invoice, payment.invoice_id)
    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Счёт не найден")

    payment.status = "SUCCESS"
    payment.external_event_id = payload.external_event_id
    invoice.status = "PAID"

    db.add(
        WebhookEvent(
            id=str(uuid4()),
            external_event_id=payload.external_event_id,
            event_type="PAYMENT_SUCCESS",
            payload=payload.model_dump(),
        )
    )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.info(
            "webhook_race_lost external_event_id=%s", payload.external_event_id
        )
        return PaymentWebhookResponse(status="already_processed")

    db.refresh(payment)
    logger.info(
        "payment_success payment_id=%s invoice_id=%s user_id=%s",
        payment.id,
        invoice.id,
        payment.user_id,
    )

    notify_payment_success(
        payment_id=payment.id,
        user_id=payment.user_id,
        invoice_id=invoice.id,
        amount_cents=payment.amount_cents,
    )

    return PaymentWebhookResponse(status="success", payment_id=payment.id)