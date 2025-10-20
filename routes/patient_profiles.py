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
from utilities.permissions import can_modify_patient_schedules
from crud import user_roles as user_roles_crud
from schemas.user_roles import UserRoleCreate
from constants.enums import UserRoleEnum
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/patients/", response_model=PatientProfileResponse)
def create_patient_profile(
    profile: PatientProfileCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # ensure the profile is created for the authenticated user
    existing_profile = profiles_crud.get_patient_profile_by_user_id(db, current_user.id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    profile.user_id = current_user.id
    created = profiles_crud.create_patient_profile(db, profile)
    # ensure the user has the PATIENT role; create if missing
    existing_roles = user_roles_crud.get_roles_for_user(db, current_user.id)
    if not any(getattr(r.role, 'value', str(r.role)) == UserRoleEnum.PATIENT.value for r in existing_roles):
        try:
            role_obj = UserRoleCreate(user_id=current_user.id, role=UserRoleEnum.PATIENT)
            user_roles_crud.create_user_role(db, role_obj)
        except IntegrityError:
            # already exists (race), ignore
            pass
    return created

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
    # Only the owner (user who created the patient profile) can update it
    if db_profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this profile")
    return profiles_crud.update_patient_profile(db, profile_id, profile)