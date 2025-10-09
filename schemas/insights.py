from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, Dict, Any

class InsightBase(BaseModel):
    period: str
    start_date: date
    end_date: date
    title: str = Field(..., min_length=5, max_length=200)
    summary: str = Field(..., min_length=10, max_length=5000)
    json_data: Optional[Dict[str, Any]] = None

class InsightCreate(InsightBase):
    patient_profile_id: int

class InsightUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    json_data: Optional[Dict[str, Any]] = None

class InsightResponse(InsightBase):
    id: int
    patient_profile_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
