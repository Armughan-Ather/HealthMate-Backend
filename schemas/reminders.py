from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional

class ReminderBase(BaseModel):
    tags: str = Field(..., min_length=1, max_length=100)
    topic: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_time: time
    start_date: date
    duration_days: int = Field(..., gt=0)
    is_active: bool = True

class ReminderCreate(ReminderBase):
    user_id: int
    created_by: Optional[int] = None

class ReminderUpdate(BaseModel):
    tags: Optional[str] = Field(None, min_length=1, max_length=100)
    topic: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    start_date: Optional[date] = None
    duration_days: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

class ReminderResponse(ReminderBase):
    id: int
    user_id: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True