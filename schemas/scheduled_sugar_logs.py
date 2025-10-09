from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional
from constants.enums import SugarTypeEnum

class SugarLogBase(BaseModel):
    value: float = Field(..., gt=0, lt=1000)
    notes: Optional[str] = None
    checked_at: Optional[datetime] = None


class SugarLogCreate(SugarLogBase):
    schedule_id: Optional[int] = None
    logged_by: Optional[int] = None


class SugarLogUpdate(BaseModel):
    value: Optional[float] = Field(None, gt=0, lt=1000)
    notes: Optional[str] = None
    checked_at: Optional[datetime] = None


class SugarScheduleSchema(BaseModel):
    id: int
    patient_profile_id: int
    scheduled_time: time
    sugar_type: SugarTypeEnum
    duration_days: Optional[int]
    start_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SugarLogOut(SugarLogBase):
    id: int
    schedule_id: Optional[int]
    patient_profile_id: Optional[int]
    logged_by: Optional[int]
    created_at: datetime
    schedule: SugarScheduleSchema

    class Config:
        from_attributes = True
