from sqlalchemy.orm import Session
from datetime import date, datetime, time
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from models.bp_schedules import BPSchedule
from schemas.bp_schedules import BPScheduleCreate, BPScheduleUpdate
from utilities.permissions import can_modify_patient_schedules
from constants.enums import FrequencyEnum, DayOfWeekEnum


def create_bp_schedule_core(
    db: Session,
    current_user,
    patient_profile_id: int,
    payload: BPScheduleCreate
) -> List[BPSchedule]:
    """
    Centralized logic for creating BP schedules.
    Shared by both /me/... and /patients/{id}/... routes.
    """
    # RBAC check
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create BP schedule for this patient."
        )

    schedules = create_bp_schedules_with_times(
        db=db,
        patient_profile_id=patient_profile_id,
        created_by=current_user.id,
        payload=payload
    )

    db.commit()
    for schedule in schedules:
        db.refresh(schedule)
    return schedules


def create_bp_schedules_with_times(
    db: Session, 
    patient_profile_id: int, 
    created_by: int, 
    payload: BPScheduleCreate
) -> List[BPSchedule]:
    """Create multiple BP schedules with different times."""
    
    if payload.duration_days is not None and payload.duration_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duration days must be positive if provided."
        )

    schedules: List[BPSchedule] = []
    
    # Convert frequency string to enum if provided
    frequency_enum = FrequencyEnum.DAILY
    if payload.frequency:
        try:
            frequency_enum = FrequencyEnum(payload.frequency)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid frequency: {payload.frequency}"
            )
    
    # Convert custom_days strings to enums if provided
    custom_days_enums = None
    if payload.custom_days:
        try:
            custom_days_enums = [DayOfWeekEnum(day) for day in payload.custom_days]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid custom_days values"
            )
    
    for scheduled_time in payload.scheduled_time:
        # Check for existing active schedule at this time
        existing = db.query(BPSchedule).filter_by(
            patient_profile_id=patient_profile_id,
            scheduled_time=scheduled_time,
            is_active=True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An active BP schedule already exists at {scheduled_time.strftime('%H:%M')}."
            )

        schedule = BPSchedule(
            patient_profile_id=patient_profile_id,
            scheduled_time=scheduled_time,
            duration_days=payload.duration_days,
            start_date=payload.start_date,
            frequency=frequency_enum,
            custom_days=custom_days_enums,
            is_active=True,
            created_by=created_by,
        )
        db.add(schedule)
        schedules.append(schedule)

    try:
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating BP schedules."
        )

    return schedules


def get_patient_bp_schedules(db: Session, patient_profile_id: int) -> List[BPSchedule]:
    """Get all BP schedules for a patient profile."""
    return db.query(BPSchedule).filter_by(patient_profile_id=patient_profile_id).all()


def count_bp_schedules(db: Session, patient_profile_id: int) -> int:
    """Count active BP schedules for a patient profile."""
    return db.query(BPSchedule).filter(
        BPSchedule.patient_profile_id == patient_profile_id,
        BPSchedule.is_active.is_(True)
    ).count()


def normalize_time(t: time) -> time:
    """Normalize time by removing seconds and microseconds."""
    return t.replace(second=0, microsecond=0, tzinfo=None)


def update_bp_schedule(db: Session, schedule_id: int, payload: BPScheduleUpdate) -> Optional[BPSchedule]:
    """Update an existing BP schedule."""
    schedule = db.query(BPSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BP schedule not found."
        )

    # Validate duration_days
    if payload.duration_days is not None:
        if payload.duration_days <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duration days must be positive."
            )
        schedule.duration_days = payload.duration_days

    # Update simple fields
    if payload.start_date is not None:
        schedule.start_date = payload.start_date

    # if payload.frequency is not None:
    #     schedule.frequency = payload.frequency

    # --- Safely update frequency and custom_days together ---
    # Safely update frequency and custom_days together
    if payload.frequency is not None or payload.custom_days is not None:
        # Determine new intended values
        new_frequency = payload.frequency or schedule.frequency
        new_custom_days = payload.custom_days if payload.custom_days is not None else schedule.custom_days

        # Convert strings to enums if necessary
        if new_custom_days is not None:
            try:
                new_custom_days = [
                    d if isinstance(d, DayOfWeekEnum) else DayOfWeekEnum(d)
                    for d in new_custom_days
                ]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid custom_days values"
                )

        # Assign both at once to bypass SQLAlchemy per-attribute validation
        object.__setattr__(schedule, "frequency", new_frequency)
        object.__setattr__(schedule, "custom_days", new_custom_days)

        # Manual consistency check (optional, safer than validator)
        if new_frequency == FrequencyEnum.DAILY and new_custom_days is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_days must be null for DAILY frequency"
            )
        if new_frequency == FrequencyEnum.WEEKLY and (not new_custom_days or len(new_custom_days) == 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_days must be provided for WEEKLY frequency"
            )
        if new_frequency == FrequencyEnum.MONTHLY and new_custom_days is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_days must be null for MONTHLY frequency"
            )



    
    # if payload.custom_days is not None:
    #     try:
    #         custom_days_enums = [DayOfWeekEnum(day) for day in payload.custom_days] if payload.custom_days else None
    #         schedule.custom_days = custom_days_enums
    #     except ValueError:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Invalid custom_days values"
    #         )
    # if payload.custom_days is not None:
    #     schedule.custom_days = payload.custom_days

    if payload.is_active is not None:
        schedule.is_active = payload.is_active

    # Handle scheduled_time change with conflict checking
    if payload.scheduled_time is not None:
        new_time = normalize_time(payload.scheduled_time)
        
        if new_time != schedule.scheduled_time:
            # Check for conflicts with other active schedules
            conflicting = db.query(BPSchedule).filter(
                BPSchedule.patient_profile_id == schedule.patient_profile_id,
                BPSchedule.scheduled_time == new_time,
                BPSchedule.is_active.is_(True),
                BPSchedule.id != schedule.id
            ).first()
            
            if conflicting:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"An active BP schedule already exists at {new_time.strftime('%H:%M')}."
                )
            
            schedule.scheduled_time = new_time

    # Commit changes with error handling
    try:
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected DB error during BP schedule update."
        )

    return schedule


def delete_bp_schedule(db: Session, schedule_id: int, patient_profile_id: int) -> bool:
    """Delete a BP schedule."""
    schedule = db.query(BPSchedule).filter_by(id=schedule_id, patient_profile_id=patient_profile_id).first()
    if not schedule:
        return False
    db.delete(schedule)
    return True