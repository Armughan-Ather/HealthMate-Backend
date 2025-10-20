from pydantic import BaseModel, Field
from typing import Optional
import datetime

class MedicationScheduleCreate(BaseModel):
    scheduled_time: datetime.time
    dosage_instruction: Optional[str] = Field(None, max_length=200)

class MedicationScheduleUpdate(BaseModel):
    scheduled_time: Optional[datetime.time] = None
    dosage_instruction: Optional[str] = Field(None, max_length=200)

class MedicationScheduleResponse(BaseModel):
    id: int
    medication_id: int
    scheduled_time: datetime.time
    dosage_instruction: Optional[str]
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
