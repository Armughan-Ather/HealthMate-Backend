from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from middlewares.auth import get_current_user
from database import get_db
from crud import doctor_profiles as profiles_crud
from schemas.doctor_profiles import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileResponse
)
from utilities.permissions import can_modify_patient_schedules
from crud import user_roles as user_roles_crud
from schemas.user_roles import UserRoleCreate
from constants.enums import UserRoleEnum
from sqlalchemy.exc import IntegrityError

router = APIRouter()

# Doctor Profile Routes
@router.post("", response_model=DoctorProfileResponse)
def create_doctor_profile(
    profile: DoctorProfileCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    existing_profile = profiles_crud.get_doctor_profile_by_user_id(db, current_user.id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    profile.user_id = current_user.id
    created = profiles_crud.create_doctor_profile(db, profile)
    # ensure the user has the DOCTOR role; create if missing
    existing_roles = user_roles_crud.get_roles_for_user(db, current_user.id)
    if not any(getattr(r.role, 'value', str(r.role)) == UserRoleEnum.DOCTOR.value for r in existing_roles):
        try:
            role_obj = UserRoleCreate(user_id=current_user.id, role=UserRoleEnum.DOCTOR)
            user_roles_crud.create_user_role(db, role_obj)
        except IntegrityError:
            pass
    return created

@router.get("/{profile_id}", response_model=DoctorProfileResponse)
def read_doctor_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    profile = profiles_crud.get_doctor_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/{profile_id}", response_model=DoctorProfileResponse)
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