from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Issue


def seed_database(session: Session) -> None:
    if session.scalar(select(Issue.id).limit(1)) is not None:
        return

    session.add(
        Issue(
            id="90000000-0000-0000-0000-000000000001",
            user_id="00000000-0000-0000-0000-000000000001",
            title="Не работает фонарь",
            description="Фонарь не включается вечером",
            category="LIGHTING",
            address="Невский проспект, 10",
            status="NEW",
        )
    )
    session.commit()
