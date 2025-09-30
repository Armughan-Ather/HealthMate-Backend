from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class WeightBase(BaseModel):
    value: float = Field(..., gt=0, lt=500)
    notes: Optional[str] = None
    measured_at: datetime

class WeightCreate(WeightBase):
    pass

class WeightUpdate(WeightBase):
    value: Optional[float] = Field(None, gt=0, lt=500)
    measured_at: Optional[datetime] = None

class WeightResponse(WeightBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True