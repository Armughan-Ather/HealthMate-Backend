from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, time
from models.sugar_schedules import SugarSchedule
from schemas.sugar_schedules import SugarScheduleUpdate, SugarScheduleCreate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from utilities.permissions import can_modify_patient_schedules
from constants.enums import FrequencyEnum, DayOfWeekEnum, SugarTypeEnum


def create_sugar_schedule_core(
    db: Session,
    current_user,
    patient_profile_id: int,
    payload: SugarScheduleCreate
):
    """
    Centralized logic for creating sugar schedules.
    Shared by both /me/... and /patients/{id}/... routes.
    """
    # RBAC check
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create sugar schedule for this patient."
        )

    schedules = create_sugar_schedules_with_times(
        db=db,
        patient_profile_id=patient_profile_id,
        created_by=current_user.id,
        payload=payload
    )

    db.commit()
    for schedule in schedules:
        db.refresh(schedule)
    return schedules


def create_sugar_schedules_with_times(db: Session, patient_profile_id: int, created_by: int, payload: SugarScheduleCreate) -> List[SugarSchedule]:
    """Create sugar schedules along with their times."""
    
    if payload.duration_days is not None and payload.duration_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duration days must be positive if provided."
        )

    # Convert frequency string to enum if provided (same as medications approach)
    frequency_enum = FrequencyEnum.DAILY
    if payload.frequency:
        try:
            frequency_enum = FrequencyEnum(payload.frequency)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid frequency: {payload.frequency}"
            )
    
    # Convert custom_days strings to enums if provided (same as medications approach)
    custom_days_enums = None
    if payload.custom_days:
        try:
            custom_days_enums = [DayOfWeekEnum(day) for day in payload.custom_days]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid custom_days values"
            )

    # Comprehensive validation in CRUD layer (since model validator is commented out)
    if frequency_enum == FrequencyEnum.DAILY and custom_days_enums is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="custom_days must be null for DAILY frequency"
        )
    elif frequency_enum == FrequencyEnum.WEEKLY and (not custom_days_enums or len(custom_days_enums) == 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="custom_days must be provided for WEEKLY frequency"
        )
    elif frequency_enum == FrequencyEnum.MONTHLY and custom_days_enums is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="custom_days must be null for MONTHLY frequency"
        )

    schedules = []
    
    for scheduled_time in payload.scheduled_time:
        # Check for existing active schedule at this time and sugar type
        existing = db.query(SugarSchedule).filter_by(
            patient_profile_id=patient_profile_id,
            scheduled_time=scheduled_time,
            sugar_type=payload.sugar_type,
            start_date=payload.start_date,
            is_active=True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A sugar schedule already exists for {scheduled_time.strftime('%H:%M')} {payload.sugar_type.value} starting on {payload.start_date}."
            )

        # Create sugar schedule with all fields (same as medications approach)
        schedule = SugarSchedule(
            patient_profile_id=patient_profile_id,
            scheduled_time=scheduled_time,
            sugar_type=payload.sugar_type,
            duration_days=payload.duration_days,
            start_date=payload.start_date,
            frequency=frequency_enum,
            custom_days=custom_days_enums,
            is_active=True,
            created_by=created_by,
        )
        
        db.add(schedule)
        
        try:
            db.flush()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating sugar schedule."
            )
        
        schedules.append(schedule)

    return schedules


def count_sugar_schedules(db: Session, patient_profile_id: int) -> int:
    return db.query(SugarSchedule).filter(
        SugarSchedule.patient_profile_id == patient_profile_id,
        SugarSchedule.is_active.is_(True)
    ).count()


def get_patient_sugar_schedules(db: Session, patient_profile_id: int) -> List[SugarSchedule]:
    """List all sugar schedules for a patient profile."""
    return db.query(SugarSchedule).filter_by(patient_profile_id=patient_profile_id).all()


def normalize_time(t: time) -> time:
    return t.replace(second=0, microsecond=0, tzinfo=None)


def update_sugar_schedule(db: Session, schedule_id: int, payload: SugarScheduleUpdate) -> Optional[SugarSchedule]:
    schedule = db.query(SugarSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sugar schedule not found."
        )

    # Validate duration_days
    if payload.duration_days is not None:
        if payload.duration_days <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duration days must be positive."
            )
        schedule.duration_days = payload.duration_days

    # Update simple fields (same as medications)
    if payload.start_date is not None:
        schedule.start_date = payload.start_date

    if payload.sugar_type is not None:
        schedule.sugar_type = payload.sugar_type

    # Handle frequency and custom_days with validation (same approach as medications)
    if payload.frequency is not None or payload.custom_days is not None:
        # Get new values
        new_frequency = payload.frequency if payload.frequency is not None else schedule.frequency
        new_custom_days = payload.custom_days if payload.custom_days is not None else schedule.custom_days
        
        # Convert strings to enums if needed
        if isinstance(new_frequency, str):
            try:
                new_frequency = FrequencyEnum(new_frequency)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid frequency: {new_frequency}"
                )
        
        if new_custom_days is not None and isinstance(new_custom_days, list):
            try:
                new_custom_days = [DayOfWeekEnum(day) if isinstance(day, str) else day for day in new_custom_days]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid custom_days values"
                )
        
        # Validate consistency (same validation as create)
        if new_frequency == FrequencyEnum.DAILY and new_custom_days is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_days must be null for DAILY frequency"
            )
        elif new_frequency == FrequencyEnum.WEEKLY and (not new_custom_days or len(new_custom_days) == 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_days must be provided for WEEKLY frequency"
            )
        elif new_frequency == FrequencyEnum.MONTHLY and new_custom_days is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_days must be null for MONTHLY frequency"
            )
        
        # Update the fields
        schedule.frequency = new_frequency
        schedule.custom_days = new_custom_days

    # Handle schedule active status
    if payload.is_active is not None:
        schedule.is_active = payload.is_active

    # Handle scheduled_time change with conflict checking
    if payload.scheduled_time is not None:
        new_time = normalize_time(payload.scheduled_time)
        
        if new_time != schedule.scheduled_time:
            # Check for conflicts with other active schedules
            conflicting = db.query(SugarSchedule).filter(
                SugarSchedule.patient_profile_id == schedule.patient_profile_id,
                SugarSchedule.scheduled_time == new_time,
                SugarSchedule.sugar_type == schedule.sugar_type,
                SugarSchedule.start_date == schedule.start_date,
                SugarSchedule.is_active.is_(True),
                SugarSchedule.id != schedule.id
            ).first()
            
            if conflicting:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A sugar schedule already exists for {new_time.strftime('%H:%M')} {schedule.sugar_type.value} starting on {schedule.start_date}."
                )
            
            schedule.scheduled_time = new_time

    # Commit changes with error handling (same as medications)
    try:
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected DB error during sugar schedule update."
        )

    return schedule


def delete_sugar_schedule(db: Session, schedule_id: int, patient_profile_id: int) -> bool:
    """Delete a sugar schedule."""
    schedule = db.query(SugarSchedule).filter_by(id=schedule_id, patient_profile_id=patient_profile_id).first()
    if not schedule:
        return False
    db.delete(schedule)
    return True


# Backward compatibility alias
def get_user_sugar_schedules(db: Session, user_id: int) -> List[SugarSchedule]:
    """
    Backward compatibility alias for get_patient_sugar_schedules.
    Used by insight_generator and other utilities.
    """
    return get_patient_sugar_schedules(db, user_id)