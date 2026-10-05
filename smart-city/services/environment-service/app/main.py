import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db, init_database
from app.models import Sensor, SensorReading
from app.schemas import SensorReadingCreate, SensorReadingResponse, SensorResponse
from app.security import verify_sensor_key
from app.seed import seed_database

SERVICE_NAME = os.getenv("SERVICE_NAME", "environment-service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    from app.database import SessionLocal

    with SessionLocal() as session:
        seed_database(session)
    logger.info("%s started", SERVICE_NAME)
    yield


app = FastAPI(title="Environment Service", lifespan=lifespan)
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


@app.get("/sensors", response_model=list[SensorResponse])
def list_sensors(db: Annotated[Session, Depends(get_db)]) -> list[Sensor]:
    return list(db.scalars(select(Sensor).order_by(Sensor.id)).all())


@app.get("/sensors/{sensor_id}/data", response_model=list[SensorReadingResponse])
def list_sensor_readings(
    sensor_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[SensorReading]:
    sensor = db.get(Sensor, sensor_id)
    if sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Датчик не найден",
        )

    return list(
        db.scalars(
            select(SensorReading)
            .where(SensorReading.sensor_id == sensor_id)
            .order_by(SensorReading.measured_at.desc(), SensorReading.id.desc())
        ).all()
    )


@app.post(
    "/sensors/data",
    response_model=SensorReadingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sensor_reading(
    payload: SensorReadingCreate,
    _: Annotated[None, Depends(verify_sensor_key)],
    db: Annotated[Session, Depends(get_db)],
) -> SensorReading:
    sensor = db.get(Sensor, payload.sensor_id)
    if sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Датчик не найден",
        )

    if sensor.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Датчик неактивен",
        )

    measured_at = payload.measured_at or datetime.now(timezone.utc)

    reading = SensorReading(
        sensor_id=sensor.id,
        value=payload.value,
        unit=payload.unit,
        measured_at=measured_at,
    )
    sensor.last_seen_at = measured_at

    db.add(reading)
    db.commit()
    db.refresh(reading)

    logger.info(
        "sensor_reading_created sensor_id=%s value=%s",
        sensor.id,
        reading.value,
    )
    return reading