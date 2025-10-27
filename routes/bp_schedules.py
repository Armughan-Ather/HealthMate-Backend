from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from database import get_db
from middlewares.auth import get_current_user, require_medical_staff, require_patient
from models.users import User
from crud import bp_schedules as bp_schedules_crud
from schemas.bp_schedules import (
    BPScheduleCreate,
    BPScheduleResponse,
    BPScheduleUpdate
)
from utilities.permissions import can_modify_patient_schedules

router = APIRouter()

# 🩺 For doctors/attendants managing a patient
@router.post("/patients/{patient_profile_id}", response_model=List[BPScheduleResponse], status_code=status.HTTP_201_CREATED)
def create_bp_schedules_for_patient(
    patient_profile_id: int, 
    payload: BPScheduleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_medical_staff)
):
    """
    Create BP schedules for a specific patient.
    Accessible by attendants and connected doctors.
    """
    return bp_schedules_crud.create_bp_schedule_core(db, current_user, patient_profile_id, payload)


@router.get("/patients/{patient_profile_id}", response_model=List[BPScheduleResponse])
def list_bp_schedules_for_patient(
    patient_profile_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_medical_staff)
):
    """List all BP schedules for a specific patient."""
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view BP schedules for this patient")
    return bp_schedules_crud.get_patient_bp_schedules(db, patient_profile_id)


@router.get("/count/{patient_profile_id}", response_model=Dict[str, int])
def count_patient_bp_schedules(
    patient_profile_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_medical_staff)
):
    """Count active BP schedules for a specific patient."""
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view BP schedules for this patient")
    active_count = bp_schedules_crud.count_bp_schedules(db, patient_profile_id)
    return {"active_count": active_count}


# 👤 For patients managing their own schedules
@router.post("", response_model=List[BPScheduleResponse], status_code=status.HTTP_201_CREATED)
def create_bp_schedules_for_self(
    payload: BPScheduleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_patient)
):
    """
    Create BP schedules for the current patient (self).
    Only accessible if the current user is a patient.
    """
    return bp_schedules_crud.create_bp_schedule_core(db, current_user, current_user.id, payload)


@router.get("", response_model=List[BPScheduleResponse])
def list_user_bp_schedules(db: Session = Depends(get_db), current_user: User = Depends(require_patient)):
    """List all BP schedules for the current user."""
    return bp_schedules_crud.get_patient_bp_schedules(db, current_user.id)


@router.get("/me/count", response_model=Dict[str, int])
def count_user_bp_schedules(db: Session = Depends(get_db), current_user: User = Depends(require_patient)):
    """Count active BP schedules for the current user."""
    active_count = bp_schedules_crud.count_bp_schedules(db, current_user.id)
    return {"active_count": active_count}


# Common endpoints for both types
@router.get("/{schedule_id}", response_model=BPScheduleResponse)
def get_bp_schedule(schedule_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a specific BP schedule by ID."""
    schedule = db.query(bp_schedules_crud.BPSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BP schedule not found")
    if not can_modify_patient_schedules(db, current_user, schedule.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this BP schedule")
    return schedule


@router.put("/{schedule_id}", response_model=BPScheduleResponse)
def update_bp_schedule(
    schedule_id: int, 
    payload: BPScheduleUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Update a specific BP schedule."""
    schedule = db.query(bp_schedules_crud.BPSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BP schedule not found")
    if not can_modify_patient_schedules(db, current_user, schedule.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this BP schedule")
    
    updated = bp_schedules_crud.update_bp_schedule(db, schedule_id, payload)
    db.commit()
    db.refresh(updated)
    return updated


@router.delete("/{schedule_id}")
def delete_bp_schedule(
    schedule_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Delete a specific BP schedule."""
    schedule = db.query(bp_schedules_crud.BPSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BP schedule not found")
    if not can_modify_patient_schedules(db, current_user, schedule.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this BP schedule")
    
    success = bp_schedules_crud.delete_bp_schedule(db, schedule_id, schedule.patient_profile_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete BP schedule")
    db.commit()
    return {"message": "BP schedule deleted"}