from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional, List
from constants.enums import ReminderTagEnum, DayOfWeekEnum, FrequencyEnum


class ReminderBase(BaseModel):
    tags: ReminderTagEnum
    topic: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    scheduled_time: time
    start_date: date
    duration_days: Optional[int] = Field(None, gt=0)
    frequency: Optional[FrequencyEnum] = None
    custom_days: Optional[List[DayOfWeekEnum]] = None
    is_active: bool = True


class ReminderCreate(ReminderBase):
    patient_profile_id: int
    created_by: int


class ReminderUpdate(BaseModel):
    tags: Optional[ReminderTagEnum] = None
    topic: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    start_date: Optional[date] = None
    duration_days: Optional[int] = Field(None, gt=0)
    frequency: Optional[str] = None
    custom_days: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ReminderResponse(ReminderBase):
    id: int
    patient_profile_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True