from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date

from models.scheduled_bp_logs import ScheduledBPLog
from models.bp_schedules import BPSchedule
from schemas.scheduled_bp_logs import ScheduledBPLogCreate, ScheduledBPLogUpdate
from utilities.permissions import can_modify_patient_logs

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

def get_active_schedule(db: Session, patient_profile_id: int, checked_date: date) -> Optional[BPSchedule]:
    return db.query(BPSchedule).filter(
        BPSchedule.patient_profile_id == patient_profile_id,
        BPSchedule.is_active == True,
        BPSchedule.start_date <= checked_date,
        # duration_days NULL means indefinite; otherwise end = start + duration_days - 1
        (
            (BPSchedule.duration_days == None) |
            (BPSchedule.start_date + (BPSchedule.duration_days - 1) >= checked_date)
        )
    ).first()


def create_bp_log(db: Session, actor_user, schedule_id: int, data: ScheduledBPLogCreate) -> Optional[ScheduledBPLog]:
    checked_at = data.checked_at or datetime.utcnow()
    checked_date = checked_at.date()

    schedule = db.query(BPSchedule).filter(BPSchedule.id == schedule_id).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found for this user."
        )
    if not can_modify_patient_logs(db, actor_user, schedule.patient_profile_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create logs for this patient")

    log = ScheduledBPLog(
        schedule_id=schedule.id,
        systolic=data.systolic,
        diastolic=data.diastolic,
        pulse=data.pulse,
        notes=data.notes,
        checked_at=checked_at,
        logged_by=getattr(actor_user, 'id', None)
    )

    try:
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except IntegrityError as e:
        db.rollback()

        # You can inspect the error string to give more specific messages
        error_message = str(e.orig)

        if "check_systolic_range" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Systolic must be between 1 and 299 and greater than diastolic."
            )
        elif "check_diastolic_range" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Diastolic must be between 1 and 199 and less than systolic."
            )
        elif "check_pulse_range" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pulse must be NULL or between 1 and 249."
            )
        elif "check_systolic_greater_than_diastolic" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Systolic must be greater than diastolic."
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blood pressure log data. Please check your input."
        )


def update_bp_log(db: Session, log_id: int, data: ScheduledBPLogUpdate) -> Optional[ScheduledBPLog]:
    log = db.query(ScheduledBPLog).filter(ScheduledBPLog.id == log_id).first()
    if not log:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(log, field, value)

    db.commit()
    db.refresh(log)
    return log


def delete_bp_log(db: Session, log_id: int) -> bool:
    log = db.query(ScheduledBPLog).filter(ScheduledBPLog.id == log_id).first()
    if not log:
        return False

    db.delete(log)
    db.commit()
    return True


def get_log_by_id(db: Session, log_id: int) -> Optional[ScheduledBPLog]:
    return db.query(ScheduledBPLog).filter(ScheduledBPLog.id == log_id).first()


def get_logs_by_schedule_id(db: Session, actor_user, schedule_id: int) -> List[ScheduledBPLog]:
    schedule = db.query(BPSchedule).filter(BPSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if not can_modify_patient_logs(db, actor_user, schedule.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(ScheduledBPLog).filter(ScheduledBPLog.schedule_id == schedule_id).order_by(ScheduledBPLog.checked_at.desc()).all()


def get_logs_by_patient_profile(db: Session, actor_user, patient_profile_id: int) -> List[ScheduledBPLog]:
    if not can_modify_patient_logs(db, actor_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(ScheduledBPLog).join(BPSchedule).filter(
        BPSchedule.patient_profile_id == patient_profile_id
    ).order_by(ScheduledBPLog.checked_at.desc()).all()

def get_recent_bp_logs(db: Session, user_id: int, limit: int = 4) -> List[ScheduledBPLog]:
    return (
        db.query(ScheduledBPLog)
        .join(BPSchedule)
        .filter(BPSchedule.user_id == user_id)
        .order_by(ScheduledBPLog.checked_at.desc())
        .limit(limit)
        .all()
    )

def get_logs_by_date_range(db: Session, actor_user, patient_profile_id: int, start_date: date, end_date: date) -> List[ScheduledBPLog]:
    # Convert date objects to datetime objects to cover the full day range
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    if not can_modify_patient_logs(db, actor_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(ScheduledBPLog).join(BPSchedule).filter(
        BPSchedule.patient_profile_id == patient_profile_id,
        ScheduledBPLog.checked_at >= start_dt,
        ScheduledBPLog.checked_at <= end_dt
    ).order_by(ScheduledBPLog.checked_at.desc()).all()


def get_logs_by_date(db: Session, actor_user, patient_profile_id: int, target_date: date) -> List[ScheduledBPLog]:
    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = datetime.combine(target_date, datetime.max.time())

    if not can_modify_patient_logs(db, actor_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(ScheduledBPLog).join(BPSchedule).filter(
        BPSchedule.patient_profile_id == patient_profile_id,
        ScheduledBPLog.checked_at >= start_dt,
        ScheduledBPLog.checked_at <= end_dt
    ).order_by(ScheduledBPLog.checked_at.desc()).all()
