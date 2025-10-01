from sqlalchemy.orm import Session
from models.patient_profiles import PatientProfile
from models.doctor_profiles import DoctorProfile
from schemas.doctor_profiles import DoctorProfileCreate, DoctorProfileUpdate, PatientProfileCreate, PatientProfileUpdate
from typing import List, Optional
from datetime import datetime

# Doctor Profile CRUD
def create_doctor_profile(db: Session, profile: DoctorProfileCreate) -> DoctorProfile:
    db_profile = DoctorProfile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_doctor_profile(db: Session, profile_id: int) -> Optional[DoctorProfile]:
    return db.query(DoctorProfile).filter(DoctorProfile.id == profile_id).first()

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

# Patient Profile CRUD
def create_patient_profile(db: Session, profile: PatientProfileCreate) -> PatientProfile:
    db_profile = PatientProfile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_patient_profile(db: Session, profile_id: int) -> Optional[PatientProfile]:
    return db.query(PatientProfile).filter(PatientProfile.id == profile_id).first()

def get_patient_profile_by_user_id(db: Session, user_id: int) -> Optional[PatientProfile]:
    return db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()

def get_all_patients(db: Session, skip: int = 0, limit: int = 100) -> List[PatientProfile]:
    return db.query(PatientProfile).offset(skip).limit(limit).all()

def update_patient_profile(db: Session, profile_id: int, profile: PatientProfileUpdate) -> Optional[PatientProfile]:
    db_profile = get_patient_profile(db, profile_id)
    if db_profile:
        update_data = profile.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_profile, field, value)
        db_profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_profile)
    return db_profile