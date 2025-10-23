from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime, date, time
from .medication_schedules import MedicationScheduleCreate
from constants.enums import FrequencyEnum

class MedicationCreateWithSchedules(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    strength: str = Field(..., min_length=1, max_length=50)
    form: str = Field(..., min_length=1, max_length=50)
    generic_name: Optional[str] = Field(None, max_length=200)
    purpose: Optional[str] = Field(None, max_length=500)
    start_date: date
    duration_days: Optional[int] = None
    schedules: List[MedicationScheduleCreate]
    frequency: Optional[str] = FrequencyEnum.DAILY.value
    custom_days: Optional[List[str]] = None

class MedicationUpdate(BaseModel):
    purpose: Optional[str] = None
    duration_days: Optional[int] = None
    start_date: Optional[date] = None
    is_active: Optional[bool] = None
    frequency: Optional[FrequencyEnum] = None
    custom_days: Optional[List[str]] = None


class MedicationScheduleResponse(BaseModel):
    id: int
    scheduled_time: time
    dosage_instruction: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class MedicineResponse(BaseModel):
    id: int
    name: str
    strength: Optional[str] = None

    class Config:
        from_attributes = True


class MedicationResponse(BaseModel):
    id: int
    patient_profile_id: int
    medicine: MedicineResponse
    purpose: Optional[str]
    duration_days: Optional[int]
    start_date: date
    is_active: bool
    frequency: Optional[str] 
    created_at: datetime
    updated_at: datetime
    schedules: List[MedicationScheduleResponse]

    class Config:
        from_attributes = True