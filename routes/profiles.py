from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_db, get_current_user
from app.crud import profiles as profiles_crud
from app.schemas.profiles import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileResponse,
    PatientProfileCreate,
    PatientProfileUpdate,
    PatientProfileResponse
)

router = APIRouter()

# Doctor Profile Routes
@router.post("/doctors/", response_model=DoctorProfileResponse)
def create_doctor_profile(
    profile: DoctorProfileCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    existing_profile = profiles_crud.get_doctor_profile_by_user_id(db, current_user.id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    return profiles_crud.create_doctor_profile(db, profile)

@router.get("/doctors/", response_model=List[DoctorProfileResponse])
def read_doctors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return profiles_crud.get_all_doctors(db, skip=skip, limit=limit)

@router.get("/doctors/{profile_id}", response_model=DoctorProfileResponse)
def read_doctor_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    profile = profiles_crud.get_doctor_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/doctors/{profile_id}", response_model=DoctorProfileResponse)
def update_doctor_profile(
    profile_id: int,
    profile: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_profile = profiles_crud.get_doctor_profile(db, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if db_profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this profile")
    return profiles_crud.update_doctor_profile(db, profile_id, profile)

# Patient Profile Routes
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