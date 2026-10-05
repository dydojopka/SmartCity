from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Parking, Vehicle

DEMO_VEHICLES = (
    {
        "id": "10000000-0000-0000-0000-000000000001",
        "plate_number": "A001AA",
        "model": "Tesla Model 3",
        "latitude": 55.7558,
        "longitude": 37.6173,
        "status": "AVAILABLE",
    },
    {
        "id": "10000000-0000-0000-0000-000000000002",
        "plate_number": "B002BB",
        "model": "Kia Rio",
        "latitude": 55.7601,
        "longitude": 37.6200,
        "status": "IN_USE",
    },
    {
        "id": "10000000-0000-0000-0000-000000000003",
        "plate_number": "C003CC",
        "model": "BMW X5",
        "latitude": 55.7500,
        "longitude": 37.6100,
        "status": "AVAILABLE",
    },
)

DEMO_PARKINGS = (
    {
        "id": "20000000-0000-0000-0000-000000000001",
        "name": "Центральная парковка",
        "address": "ул. Тверская, 1",
        "latitude": 55.7570,
        "longitude": 37.6150,
        "total_spaces": 10,
        "available_spaces": 10,
        "price_per_hour_cents": 20000,
    },
    {
        "id": "20000000-0000-0000-0000-000000000002",
        "name": "Парковка у парка",
        "address": "ул. Парковая, 10",
        "latitude": 55.7300,
        "longitude": 37.6000,
        "total_spaces": 5,
        "available_spaces": 5,
        "price_per_hour_cents": 15000,
    },
)


def seed_database(session: Session) -> None:
    if session.scalar(select(Vehicle.id).limit(1)) is None:
        for vehicle in DEMO_VEHICLES:
            session.add(Vehicle(**vehicle))

    if session.scalar(select(Parking.id).limit(1)) is None:
        for parking in DEMO_PARKINGS:
            session.add(Parking(**parking))

    session.commit()