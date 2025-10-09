from pydantic import BaseModel
import datetime
from typing import Optional, List


class BPScheduleCreate(BaseModel):
    scheduled_time: List[datetime.time]
    start_date: datetime.date
    duration_days: Optional[int] = None
    frequency: Optional[str] = None
    custom_days: Optional[List[str]] = None


class BPScheduleUpdate(BaseModel):
    scheduled_time: Optional[datetime.time] = None
    start_date: Optional[datetime.date] = None
    duration_days: Optional[int] = None
    frequency: Optional[str] = None
    custom_days: Optional[List[str]] = None
    is_active: Optional[bool] = None


class BPScheduleResponse(BaseModel):
    id: int
    patient_profile_id: int
    scheduled_time: datetime.time
    duration_days: Optional[int]
    start_date: datetime.date
    frequency: str
    custom_days: Optional[List[str]]
    is_active: bool
    created_by: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True