from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import Optional
from enum import Enum

class ReminderType(str, Enum):
    MEDICINE = "medicine"
    APPOINTMENT = "appointment"
    GENERAL = "general"

class ReminderBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    reminder_type: ReminderType
    scheduled_time: time
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(ReminderBase):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    reminder_type: Optional[ReminderType] = None
    scheduled_time: Optional[time] = None

class ReminderResponse(ReminderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True