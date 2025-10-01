from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from middlewares.auth import get_current_user
from database import get_db
from crud import patient_profiles as profiles_crud
from schemas.patient_profiles import (
    PatientProfileCreate,
    PatientProfileUpdate,
    PatientProfileResponse
)

router = APIRouter()

@router.post("/patients/", response_model=PatientProfileResponse)
def create_patient_profile(
    profile: PatientProfileCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    existing_profile = profiles_crud.get_patient_profile_by_user_id(db, current_user.id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    return profiles_crud.create_patient_profile(db, profile)

@router.get("/patients/", response_model=List[PatientProfileResponse])
def read_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return profiles_crud.get_all_patients(db, skip=skip, limit=limit)

@router.get("/patients/{profile_id}", response_model=PatientProfileResponse)
def read_patient_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    profile = profiles_crud.get_patient_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/patients/{profile_id}", response_model=PatientProfileResponse)
def update_patient_profile(
    profile_id: int,
    profile: PatientProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_profile = profiles_crud.get_patient_profile(db, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if db_profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this profile")
    return profiles_crud.update_patient_profile(db, profile_id, profile)