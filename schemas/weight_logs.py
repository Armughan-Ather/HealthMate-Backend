from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class WeightBase(BaseModel):
    value: float = Field(..., gt=0, lt=500)
    notes: Optional[str] = None
    measured_at: datetime
    patient_id: int

class WeightCreate(WeightBase):
    pass

class WeightUpdate(BaseModel):
    value: Optional[float] = Field(None, gt=0, lt=500)
    notes: Optional[str] = None
    measured_at: Optional[datetime] = None

class WeightResponse(WeightBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True