from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ReservationStatus = Literal["ACTIVE", "CANCELLED", "EXPIRED"]


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plate_number: str
    model: str
    latitude: float
    longitude: float
    status: str
    created_at: datetime


class ParkingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    total_spaces: int
    available_spaces: int
    price_per_hour_cents: int


class ParkingReserveRequest(BaseModel):
    expires_in_minutes: int = Field(default=30, ge=1, le=24 * 60)


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parking_id: str
    user_id: str
    status: ReservationStatus
    created_at: datetime
    expires_at: datetime | None