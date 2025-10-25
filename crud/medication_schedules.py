from sqlalchemy.orm import Session
from typing import List, Optional
from models.medication_schedules import MedicationSchedule
from schemas.medication_schedules import MedicationScheduleUpdate
from fastapi import HTTPException

def get_schedules_for_medication(db: Session, medication_id: int) -> List[MedicationSchedule]:
    """Get all schedules for a given medication."""
    return db.query(MedicationSchedule).filter_by(medication_id=medication_id).all()


def create_medication_schedule(db: Session, medication_id: int, scheduled_time, dosage_instruction) -> MedicationSchedule:
    """Create or reactivate a medication schedule."""
    existing_active = db.query(MedicationSchedule).filter_by(
        medication_id=medication_id,
        scheduled_time=scheduled_time,
        is_active=True
    ).first()

    if existing_active:
        raise HTTPException(status_code=400, detail="An active schedule already exists at this time.")

    existing_inactive = db.query(MedicationSchedule).filter_by(
        medication_id=medication_id,
        scheduled_time=scheduled_time,
        is_active=False
    ).first()

    if existing_inactive:
        # Reactivate the inactive schedule
        existing_inactive.is_active = True
        existing_inactive.dosage_instruction = dosage_instruction
        db.flush()
        return existing_inactive

    # Otherwise, create a new schedule
    schedule = MedicationSchedule(
        medication_id=medication_id,
        scheduled_time=scheduled_time,
        dosage_instruction=dosage_instruction
    )
    db.add(schedule)
    db.flush()
    return schedule


def update_medication_schedule(db: Session, schedule_id: int, payload: MedicationScheduleUpdate) -> Optional[MedicationSchedule]:
    """Update an existing medication schedule with de-duplication logic."""
    schedule = db.query(MedicationSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        return None

    new_time = payload.scheduled_time or schedule.scheduled_time

    # If schedule time is changing, check conflicts
    if new_time != schedule.scheduled_time:
        conflicting_active = db.query(MedicationSchedule).filter_by(
            medication_id=schedule.medication_id,
            scheduled_time=new_time,
            is_active=True
        ).first()

        if conflicting_active:
            raise HTTPException(status_code=400, detail="An active schedule already exists for this time.")

        conflicting_inactive = db.query(MedicationSchedule).filter_by(
            medication_id=schedule.medication_id,
            scheduled_time=new_time,
            is_active=False
        ).first()

        if conflicting_inactive:
            # Clean up old inactive one
            db.delete(conflicting_inactive)

        schedule.scheduled_time = new_time

    if payload.dosage_instruction is not None:
        schedule.dosage_instruction = payload.dosage_instruction

    db.flush()
    return schedule


def delete_medication_schedule(db: Session, schedule_id: int) -> bool:
    """Delete a medication schedule."""
    schedule = db.query(MedicationSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        return False
    db.delete(schedule)
    return True
