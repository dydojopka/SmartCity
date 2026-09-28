from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models import User

DEMO_PASSWORD = "demo12345"
DEMO_USERS = (
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "user@smartcity.local",
        "first_name": "Иван",
        "last_name": "Петров",
        "role": "USER",
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "email": "operator@smartcity.local",
        "first_name": "Анна",
        "last_name": "Смирнова",
        "role": "OPERATOR",
    },
    {
        "id": "00000000-0000-0000-0000-000000000003",
        "email": "admin@smartcity.local",
        "first_name": "Павел",
        "last_name": "Волков",
        "role": "ADMIN",
    },
)


def seed_database(session: Session) -> None:
    if session.scalar(select(User.id).limit(1)) is not None:
        return

    for user_data in DEMO_USERS:
        session.add(User(**user_data, password_hash=hash_password(DEMO_PASSWORD)))
    session.commit()
