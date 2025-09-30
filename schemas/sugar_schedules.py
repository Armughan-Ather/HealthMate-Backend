from pydantic import BaseModel, Field
import datetime
from typing import Optional, List
from models.sugar_logs import SugarType

class SugarScheduleCreate(BaseModel):
    times: List[datetime.time]
    sugar_type: SugarType
    start_date: Optional[datetime.date]
    end_date: datetime.date

class SugarScheduleUpdate(BaseModel):
    time: Optional[datetime.time] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    is_active: Optional[bool] = None

class SugarScheduleResponse(BaseModel):
    id: int
    user_id: int
    time: datetime.time
    sugar_type: SugarType
    duration_days: int
    start_date: datetime.date
    end_date: Optional[datetime.date]
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True