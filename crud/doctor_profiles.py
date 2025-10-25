from sqlalchemy.orm import Session
from models.doctor_profiles import DoctorProfile
from schemas.doctor_profiles import DoctorProfileCreate, DoctorProfileUpdate
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException
from models.user_roles import UserRole
from constants.enums import UserRoleEnum

def create_doctor_profile(db: Session, profile: DoctorProfileCreate, user_id: int) -> DoctorProfile:
    db_profile = DoctorProfile(**profile.model_dump(), user_id=user_id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_doctor_profile(db: Session, profile_id: int) -> Optional[DoctorProfile]:
    profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

def get_doctor_profile_by_user_id(db: Session, user_id: int) -> Optional[DoctorProfile]:
    return db.query(DoctorProfile).filter(DoctorProfile.user_id == user_id).first()

def get_all_doctors(db: Session, skip: int = 0, limit: int = 100) -> List[DoctorProfile]:
    return db.query(DoctorProfile).offset(skip).limit(limit).all()

def update_doctor_profile(db: Session, profile_id: int, profile: DoctorProfileUpdate) -> Optional[DoctorProfile]:
    db_profile = get_doctor_profile(db, profile_id)
    if db_profile:
        update_data = profile.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_profile, field, value)
        db_profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_profile)
    return db_profile

def delete_doctor_profile(db: Session, user_id: int):
    profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role == UserRoleEnum.DOCTOR
    ).delete()
    db.delete(profile)
    db.commit()
    return True