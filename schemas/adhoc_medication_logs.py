from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Nested schemas
class MedicineSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class PatientProfileSchema(BaseModel):
    user_id: int

    class Config:
        from_attributes = True

# Base schemas
class AdhocMedicationLogBase(BaseModel):
    medicine_id: int
    dosage_taken: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    taken_at: datetime

class AdhocMedicationLogCreate(AdhocMedicationLogBase):
    patient_profile_id: int

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
    medicine: MedicineSchema
    patient: PatientProfileSchema

    class Config:
        from_attributes = True
