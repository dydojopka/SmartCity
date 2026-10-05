from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Sensor


def seed_database(session: Session) -> None:
    if session.scalar(select(Sensor.id).limit(1)) is not None:
        return

    session.add_all(
        [
            Sensor(
                name="Температура воздуха",
                type="TEMPERATURE",
                location="Центр города",
                status="ACTIVE",
            ),
            Sensor(
                name="Влажность воздуха",
                type="HUMIDITY",
                location="Городской парк",
                status="ACTIVE",
            ),
        ]
    )
    session.commit()