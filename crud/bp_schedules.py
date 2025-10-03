from sqlalchemy.orm import Session
from datetime import date, datetime
from models.bp_schedules import BloodPressureSchedule
from typing import List, Optional
from schemas.bp_schedules import BPScheduleCreate, BPScheduleUpdate, BPScheduleResponse
from fastapi import HTTPException, status

def get_user_bp_schedules(db: Session, user_id: int) -> List[BloodPressureSchedule]:
    return db.query(BloodPressureSchedule).filter_by(user_id=user_id).all()

def create_bp_schedule(db: Session, user_id: int, payload: BPScheduleCreate) -> BloodPressureSchedule:
    start_date = payload.start_date or date.today()
    end_date = payload.end_date

    if not end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date is required."
        )

    duration_days = (end_date - start_date).days + 1
    if duration_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after or equal to start date."
        )

    db_schedule = BloodPressureSchedule(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        frequency_hours=payload.frequency_hours,
        target_systolic=payload.target_systolic,
        target_diastolic=payload.target_diastolic,
        notes=payload.notes
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update_bp_schedule(db: Session, schedule_id: int, payload: BPScheduleUpdate) -> Optional[BloodPressureSchedule]:
    db_schedule = db.query(BloodPressureSchedule).filter_by(id=schedule_id).first()
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
    db_schedule = db.query(BloodPressureSchedule).filter_by(id=schedule_id).first()
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    db.delete(db_schedule)
    db.commit()
    return True
