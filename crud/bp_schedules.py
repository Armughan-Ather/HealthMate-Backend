from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List, Optional
from fastapi import HTTPException, status

from models.bp_schedules import BPSchedule
from schemas.bp_schedules import BPScheduleCreate, BPScheduleUpdate
from utilities.permissions import can_modify_patient_schedules

def get_patient_bp_schedules(db: Session, patient_profile_id: int) -> List[BPSchedule]:
    return db.query(BPSchedule).filter_by(patient_profile_id=patient_profile_id).all()

def create_bp_schedules(db: Session, patient_profile_id: int, created_by: int, payload: BPScheduleCreate) -> List[BPSchedule]:
    start_date = payload.start_date or date.today()
    duration_days = payload.duration_days

    if duration_days is not None and duration_days <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="duration_days must be positive if provided")

    schedules: List[BPSchedule] = []
    for t in payload.scheduled_time:
        schedule = BPSchedule(
            patient_profile_id=patient_profile_id,
            scheduled_time=t,
            duration_days=duration_days,
            start_date=start_date,
            # frequency and custom_days are optional; model defaults handle validation if provided
            frequency=payload.frequency if getattr(payload, 'frequency', None) else None,
            custom_days=payload.custom_days if getattr(payload, 'custom_days', None) else None,
            is_active=True,
            created_by=created_by,
        )
        db.add(schedule)
        schedules.append(schedule)

    db.commit()
    for s in schedules:
        db.refresh(s)
    return schedules

def update_bp_schedule(db: Session, schedule_id: int, payload: BPScheduleUpdate) -> Optional[BPSchedule]:
    db_schedule = db.query(BPSchedule).filter_by(id=schedule_id).first()
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_schedule, field, value)
    
    db_schedule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_bp_schedule(db: Session, schedule_id: int) -> bool:
    db_schedule = db.query(BPSchedule).filter_by(id=schedule_id).first()
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    db.delete(db_schedule)
    db.commit()
    return True
