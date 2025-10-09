from pydantic import BaseModel
import datetime
from typing import Optional, List
from constants.enums import SugarTypeEnum

class SugarScheduleCreate(BaseModel):
    scheduled_times: List[datetime.time]
    sugar_type: SugarTypeEnum
    start_date: Optional[datetime.date]
    duration_days: Optional[int] = None

class SugarScheduleUpdate(BaseModel):
    scheduled_time: Optional[datetime.time] = None
    start_date: Optional[datetime.date] = None
    duration_days: Optional[int] = None
    is_active: Optional[bool] = None


class SugarScheduleResponse(BaseModel):
    id: int
    patient_profile_id: int
    scheduled_time: datetime.time
    sugar_type: Optional[SugarTypeEnum]
    duration_days: Optional[int]
    start_date: datetime.date
    is_active: bool
    created_by: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True