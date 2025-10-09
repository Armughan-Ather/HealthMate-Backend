from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WeightBase(BaseModel):
    weight: float = Field(..., gt=0, lt=1000)
    unit: Optional[str] = None
    notes: Optional[str] = None
    checked_at: datetime
    patient_profile_id: int


class WeightCreate(WeightBase):
    logged_by: Optional[int] = None


class WeightUpdate(BaseModel):
    weight: Optional[float] = Field(None, gt=0, lt=1000)
    unit: Optional[str] = None
    notes: Optional[str] = None
    checked_at: Optional[datetime] = None


class WeightResponse(WeightBase):
    id: int
    logged_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True