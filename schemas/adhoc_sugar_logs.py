from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AdhocSugarLogBase(BaseModel):
    value: float = Field(..., gt=0, lt=1000)
    type: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)
    checked_at: datetime

class AdhocSugarLogCreate(AdhocSugarLogBase):
    patient_profile_id: int
    logged_by: int

class AdhocSugarLogUpdate(BaseModel):
    value: Optional[float] = Field(None, gt=0, lt=1000)
    notes: Optional[str] = Field(None, max_length=500)
    checked_at: Optional[datetime] = None

class AdhocSugarLogResponse(AdhocSugarLogBase):
    id: int
    patient_profile_id: int
    logged_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
