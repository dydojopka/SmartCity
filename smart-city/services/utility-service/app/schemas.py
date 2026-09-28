from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IssueStatus = Literal["NEW", "IN_PROGRESS", "RESOLVED", "REJECTED"]


class IssueCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3, max_length=5000)
    category: str = Field(min_length=2, max_length=50)
    address: str = Field(min_length=3, max_length=300)


class IssueStatusUpdate(BaseModel):
    status: IssueStatus


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    description: str
    category: str
    address: str
    status: IssueStatus
    created_at: datetime
    updated_at: datetime
