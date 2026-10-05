from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Invoice

# UUID совпадают с identity-service/app/seed.py
USER_IVAN = "00000000-0000-0000-0000-000000000001"   # USER
USER_ANNA = "00000000-0000-0000-0000-000000000002"   # OPERATOR
USER_PAVEL = "00000000-0000-0000-0000-000000000003"  # ADMIN

DEMO_INVOICES = (
    {
        "id": "50000000-0000-0000-0000-000000000001",
        "user_id": USER_IVAN,
        "amount_cents": 150000,
        "status": "UNPAID",
        "description": "Коммунальные услуги за месяц",
    },
    {
        "id": "50000000-0000-0000-0000-000000000002",
        "user_id": USER_IVAN,
        "amount_cents": 50000,
        "status": "UNPAID",
        "description": "Парковочный абонемент",
    },
    {
        "id": "50000000-0000-0000-0000-000000000003",
        "user_id": USER_ANNA,
        "amount_cents": 99000,
        "status": "UNPAID",
        "description": "Электроэнергия",
    },
    {
        "id": "50000000-0000-0000-0000-000000000004",
        "user_id": USER_PAVEL,
        "amount_cents": 250000,
        "status": "UNPAID",
        "description": "Аренда офиса",
    },
)


def seed_database(session: Session) -> None:
    if session.scalar(select(Invoice.id).limit(1)) is not None:
        return

    for invoice in DEMO_INVOICES:
        session.add(Invoice(**invoice))
    session.commit()