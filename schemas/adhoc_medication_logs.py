from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AdhocMedicationLogBase(BaseModel):
    medicine_id: int
    dosage_taken: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    taken_at: datetime

class AdhocMedicationLogCreate(AdhocMedicationLogBase):
    patient_profile_id: int
    logged_by: int

class AdhocMedicationLogUpdate(BaseModel):
    dosage_taken: Optional[str] = Field(None, min_length=1, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    taken_at: Optional[datetime] = None

class AdhocMedicationLogResponse(AdhocMedicationLogBase):
    id: int
    patient_profile_id: int
    logged_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
