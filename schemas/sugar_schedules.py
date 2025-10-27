from pydantic import BaseModel
import datetime
from typing import Optional, List
from constants.enums import SugarTypeEnum, FrequencyEnum, DayOfWeekEnum

class SugarScheduleCreate(BaseModel):
    scheduled_time: List[datetime.time]  # Changed from scheduled_times to match BP schedules
    sugar_type: SugarTypeEnum
    start_date: datetime.date
    duration_days: Optional[int] = None
    frequency: Optional[str] = None
    custom_days: Optional[List[str]] = None

class SugarScheduleUpdate(BaseModel):
    scheduled_time: Optional[datetime.time] = None
    sugar_type: Optional[SugarTypeEnum] = None
    start_date: Optional[datetime.date] = None
    duration_days: Optional[int] = None
    frequency: Optional[FrequencyEnum] = None
    custom_days: Optional[List[DayOfWeekEnum]] = None
    is_active: Optional[bool] = None


class SugarScheduleResponse(BaseModel):
    id: int
    patient_profile_id: int
    scheduled_time: datetime.time
    sugar_type: SugarTypeEnum
    duration_days: Optional[int]
    start_date: datetime.date
    frequency: FrequencyEnum  # Changed from str to FrequencyEnum to match BP schedules
    custom_days: Optional[List[str]]
    is_active: bool
    created_by: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True