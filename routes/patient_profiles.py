from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from middlewares.auth import get_current_user, get_current_user_without_role, require_patient, require_attendant, require_medical_staff, require_doctor
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
from typing import Optional

router = APIRouter()

@router.post("", response_model=PatientProfileResponse)
def create_patient_profile(
    profile: PatientProfileCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_without_role)
):
    # ensure the profile is created for the authenticated user
    existing_profile = profiles_crud.get_patient_profile_by_user_id(db, current_user.id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    created = profiles_crud.create_patient_profile(db, profile, current_user.id)
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

# for attendants and doctors to view patient profiles
@router.get("/{patient_profile_id}", response_model=PatientProfileResponse)
def read_patient_profile(
    patient_profile_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to get profile of this patient")
    profile = profiles_crud.get_patient_profile(db, patient_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.get("", response_model=PatientProfileResponse)
def read_patient_profile(
    db: Session = Depends(get_db),
    current_user = Depends(require_patient)
):
    profile = profiles_crud.get_patient_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("", response_model=PatientProfileResponse)
def update_patient_profile(
    profile: PatientProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_patient)
):
    db_profile = profiles_crud.get_patient_profile(db, current_user.id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profiles_crud.update_patient_profile(db, current_user.id, profile)

@router.delete("", status_code=204)
def delete_patient_profile(
    db: Session = Depends(get_db),
    current_user = Depends(require_patient)
):
    profiles_crud.delete_patient_profile(db, current_user.id)
    return {"detail": "Profile deleted successfully"}