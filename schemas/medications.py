from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime, date, time
from .medication_schedules import MedicationScheduleCreate, MedicationScheduleResponse
from .medicines import MedicineResponse
from constants.enums import FrequencyEnum, DayOfWeekEnum

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
    custom_days: Optional[List[DayOfWeekEnum]] = None

class MedicationUpdate(BaseModel):
    purpose: Optional[str] = None
    duration_days: Optional[int] = None
    start_date: Optional[date] = None
    is_active: Optional[bool] = None
    frequency: Optional[FrequencyEnum] = None
    custom_days: Optional[List[DayOfWeekEnum]] = None
    schedules: List[MedicationScheduleCreate]

class MedicationResponse(BaseModel):
    id: int
    patient_profile_id: int
    medicine: MedicineResponse
    purpose: Optional[str]
    duration_days: Optional[int]
    start_date: date
    is_active: bool
    frequency: FrequencyEnum
    custom_days: Optional[List[DayOfWeekEnum]] 
    created_at: datetime
    updated_at: datetime
    schedules: List[MedicationScheduleResponse]

    class Config:
        from_attributes = True