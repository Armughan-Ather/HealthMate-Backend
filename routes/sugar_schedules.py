from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from database import get_db
from middlewares.auth import get_current_user, require_medical_staff, require_patient
from models.users import User
from crud import sugar_schedules as sugar_schedules_crud
from schemas.sugar_schedules import (
    SugarScheduleCreate,
    SugarScheduleResponse,
    SugarScheduleUpdate
)
from utilities.permissions import can_modify_patient_schedules

router = APIRouter()

# 🩺 For doctors/attendants managing a patient
@router.post("/patients/{patient_profile_id}", response_model=List[SugarScheduleResponse], status_code=status.HTTP_201_CREATED)
def create_sugar_schedules_for_patient(
    patient_profile_id: int, 
    payload: SugarScheduleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_medical_staff)
):
    """
    Create sugar schedules for a specific patient.
    Accessible by attendants and connected doctors.
    """
    return sugar_schedules_crud.create_sugar_schedule_core(db, current_user, patient_profile_id, payload)


@router.get("/patients/{patient_profile_id}", response_model=List[SugarScheduleResponse])
def list_sugar_schedules_for_patient(
    patient_profile_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_medical_staff)
):
    """List all sugar schedules for a specific patient."""
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view sugar schedules for this patient")
    return sugar_schedules_crud.get_patient_sugar_schedules(db, patient_profile_id)


@router.get("/count/{patient_profile_id}", response_model=Dict[str, int])
def count_patient_sugar_schedules(
    patient_profile_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_medical_staff)
):
    """Count active sugar schedules for a specific patient."""
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view sugar schedules for this patient")
    active_count = sugar_schedules_crud.count_sugar_schedules(db, patient_profile_id)
    return {"active_count": active_count}


# 👤 For patients managing their own schedules
@router.post("", response_model=List[SugarScheduleResponse], status_code=status.HTTP_201_CREATED)
def create_sugar_schedules_for_self(
    payload: SugarScheduleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_patient)
):
    """
    Create sugar schedules for the current patient (self).
    Only accessible if the current user is a patient.
    """
    return sugar_schedules_crud.create_sugar_schedule_core(db, current_user, current_user.id, payload)


@router.get("", response_model=List[SugarScheduleResponse])
def list_user_sugar_schedules(db: Session = Depends(get_db), current_user: User = Depends(require_patient)):
    """List all sugar schedules for the current user."""
    return sugar_schedules_crud.get_patient_sugar_schedules(db, current_user.id)


@router.get("/me/count", response_model=Dict[str, int])
def count_user_sugar_schedules(db: Session = Depends(get_db), current_user: User = Depends(require_patient)):
    """Count active sugar schedules for the current user."""
    active_count = sugar_schedules_crud.count_sugar_schedules(db, current_user.id)
    return {"active_count": active_count}


# Common endpoints for both types
@router.get("/{schedule_id}", response_model=SugarScheduleResponse)
def get_sugar_schedule(schedule_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a specific sugar schedule by ID."""
    schedule = db.query(sugar_schedules_crud.SugarSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugar schedule not found")
    if not can_modify_patient_schedules(db, current_user, schedule.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this sugar schedule")
    return schedule


@router.put("/{schedule_id}", response_model=SugarScheduleResponse)
def update_sugar_schedule(
    schedule_id: int, 
    payload: SugarScheduleUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Update a specific sugar schedule."""
    schedule = db.query(sugar_schedules_crud.SugarSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugar schedule not found")
    if not can_modify_patient_schedules(db, current_user, schedule.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this sugar schedule")
    
    updated = sugar_schedules_crud.update_sugar_schedule(db, schedule_id, payload)
    db.commit()
    db.refresh(updated)
    return updated


@router.delete("/{schedule_id}")
def delete_sugar_schedule(
    schedule_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Delete a specific sugar schedule."""
    schedule = db.query(sugar_schedules_crud.SugarSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sugar schedule not found")
    if not can_modify_patient_schedules(db, current_user, schedule.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this sugar schedule")
    
    success = sugar_schedules_crud.delete_sugar_schedule(db, schedule_id, schedule.patient_profile_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete sugar schedule")
    db.commit()
    return {"message": "Sugar schedule deleted"}