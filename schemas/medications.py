from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime, date, time


class MedicationScheduleCreate(BaseModel):
    scheduled_time: time
    dosage_instruction: Optional[str] = Field(None, min_length=1, max_length=200)

class MedicationCreateWithSchedules(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    strength: str = Field(..., min_length=1, max_length=50)
    form: str = Field(..., min_length=1, max_length=50)
    generic_name: Optional[str] = Field(None, max_length=200)
    purpose: Optional[str] = Field(None, max_length=500)
    start_date: date
    patient_profile_id: int
    medicine_id: Optional[int] = None
    prescribed_by: int
    duration_days: Optional[int] = None
    schedules: List[MedicationScheduleCreate]
    frequency: Optional[str] = None
    custom_days: Optional[List[str]] = None

    @model_validator(mode='before')
    def validate_dates(cls, values):
        start = values.get("start_date")
        end = values.get("end_date")
        if start and end and end < start:
            raise ValueError("End date must be greater than or equal to start date")
        return values

class MedicationUpdate(BaseModel):
    purpose: Optional[str] = None
    duration_days: Optional[int] = None
    start_date: Optional[date] = None
    is_active: Optional[bool] = None
    frequency: Optional[str] = None
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
    created_at: datetime
    updated_at: datetime
    schedules: List[MedicationScheduleResponse]

    class Config:
        from_attributes = True