from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AdhocBPLogBase(BaseModel):
    systolic: int = Field(..., gt=0, lt=1000)
    diastolic: int = Field(..., gt=0, lt=1000)
    pulse: Optional[int] = Field(None, gt=0, lt=1000)
    notes: Optional[str] = Field(None, max_length=500)
    checked_at: datetime

class AdhocBPLogCreate(AdhocBPLogBase):
    patient_profile_id: int
    logged_by: int

class AdhocBPLogUpdate(BaseModel):
    systolic: Optional[int] = Field(None, gt=0, lt=1000)
    diastolic: Optional[int] = Field(None, gt=0, lt=1000)
    pulse: Optional[int] = Field(None, gt=0, lt=1000)
    notes: Optional[str] = Field(None, max_length=500)
    checked_at: Optional[datetime] = None

class AdhocBPLogResponse(AdhocBPLogBase):
    id: int
    patient_profile_id: int
    logged_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
