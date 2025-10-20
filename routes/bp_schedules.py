from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from middlewares.auth import get_current_user
from schemas.bp_schedules import BPScheduleCreate, BPScheduleUpdate, BPScheduleResponse
from crud.bp_schedules import (
    get_patient_bp_schedules,
    create_bp_schedules,
    update_bp_schedule,
    delete_bp_schedule
)
from models.bp_schedules import BPSchedule
from models.users import User
from utilities.permissions import can_modify_patient_schedules

router = APIRouter()

@router.get("/patients/{patient_profile_id}", response_model=List[BPScheduleResponse])
def list_bp_schedules_for_patient(patient_profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view BP schedules for this patient")
    return get_patient_bp_schedules(db, patient_profile_id)

@router.post("/patients/{patient_profile_id}", response_model=List[BPScheduleResponse], status_code=201)
def create_schedules_for_patient(patient_profile_id: int, payload: BPScheduleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to create BP schedules for this patient")
    schedules = create_bp_schedules(db, patient_profile_id, current_user.id, payload)
    return schedules

@router.put("/{schedule_id}", response_model=BPScheduleResponse)
def update_schedule(schedule_id: int, payload: BPScheduleUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    schedule = update_bp_schedule(db, schedule_id, payload)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.commit()
    db.refresh(schedule)
    return schedule

@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    success = delete_bp_schedule(db, schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.commit()
    return