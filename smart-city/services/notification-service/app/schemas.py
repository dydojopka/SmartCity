from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    user_id: str | None = None
    recipient: str = Field(min_length=1, max_length=255)
    channel: str = Field(min_length=1, max_length=50)
    subject: str | None = Field(default=None, max_length=255)
    message: str = Field(min_length=1)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str | None
    recipient: str
    channel: str
    subject: str | None
    message: str
    status: Literal["PENDING", "SENT", "FAILED"]
    created_at: datetime
    sent_at: datetime | None