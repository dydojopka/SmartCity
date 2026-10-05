from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SensorStatus = Literal["ACTIVE", "INACTIVE", "MAINTENANCE"]


class SensorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    location: str | None
    status: SensorStatus
    last_seen_at: datetime | None
    created_at: datetime


class SensorReadingCreate(BaseModel):
    sensor_id: int
    value: float
    unit: str | None = None
    measured_at: datetime | None = None


class SensorReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sensor_id: int
    value: float
    unit: str | None
    measured_at: datetime
    created_at: datetime