from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from middlewares.auth import get_current_user, get_current_user_without_role, require_doctor
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
from models.users import User

router = APIRouter()

# Doctor Profile Routes
@router.post("", response_model=DoctorProfileResponse)
def create_doctor_profile(
    profile: DoctorProfileCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_without_role)
):
    existing_profile = profiles_crud.get_doctor_profile_by_user_id(db, current_user.id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    created = profiles_crud.create_doctor_profile(db, profile, current_user.id)
    role_obj = UserRoleCreate(user_id=current_user.id, role=UserRoleEnum.DOCTOR)
    user_roles_crud.create_user_role(db, role_obj, current_user.id)
    return created

@router.get("", response_model=DoctorProfileResponse)
def read_my_doctor_profile(
    db: Session = Depends(get_db),
    current_user = Depends(require_doctor)
):
    return profiles_crud.get_doctor_profile(db, current_user.id)

@router.get("/{profile_id}", response_model=DoctorProfileResponse)
def read_doctor_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return profiles_crud.get_doctor_profile(db, profile_id)

@router.put("", response_model=DoctorProfileResponse)
def update_doctor_profile(
    profile: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    db_profile = profiles_crud.get_doctor_profile(db, current_user.id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if db_profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this profile")
    return profiles_crud.update_doctor_profile(db, current_user.id, profile)

@router.delete("", status_code=204)
def delete_doctor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    profiles_crud.delete_doctor_profile(db, current_user.id)
    return {"detail": "Profile deleted successfully"}