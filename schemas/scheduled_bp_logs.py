from pydantic import BaseModel, Field
from datetime import datetime, time, date
from typing import Optional

class ScheduledBPLogBase(BaseModel):
    systolic: int = Field(..., gt=0, lt=1000)
    diastolic: int = Field(..., gt=0, lt=1000)
    pulse: Optional[int] = Field(None, gt=0, lt=1000)
    notes: Optional[str] = Field(None, max_length=500)
    checked_at: datetime

class ScheduledBPLogCreate(ScheduledBPLogBase):
    schedule_id: int
    logged_by: Optional[int] = None

class ScheduledBPLogUpdate(BaseModel):
    systolic: Optional[int] = Field(None, gt=0, lt=1000)
    diastolic: Optional[int] = Field(None, gt=0, lt=1000)
    pulse: Optional[int] = Field(None, gt=0, lt=1000)
    notes: Optional[str] = Field(None, max_length=500)
    checked_at: Optional[datetime] = None

class BPScheduleSchema(BaseModel):
    id: int
    patient_profile_id: int
    scheduled_time: time
    duration_days: Optional[int]
    start_date: date
    frequency: str
    custom_days: Optional[list]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ScheduledBPLogResponse(ScheduledBPLogBase):
    id: int
    schedule: BPScheduleSchema
    logged_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True