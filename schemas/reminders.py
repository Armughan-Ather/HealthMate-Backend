from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional
from enum import Enum

class ReminderTagEnum(str, Enum):
    APPOINTMENT = "APPOINTMENT"
    WATER = "WATER"
    EXERCISE = "EXERCISE"
    SLEEP = "SLEEP"
    MEAL = "MEAL"
    LAB_TEST = "LAB_TEST"
    THERAPY = "THERAPY"
    VACCINATION = "VACCINATION"

class ReminderBase(BaseModel):
    tags: ReminderTagEnum
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
    tags: Optional[ReminderTagEnum] = None
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