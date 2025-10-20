from sqlalchemy.orm import Session
from typing import List, Optional
from models.medication_schedules import MedicationSchedule
from schemas.medication_schedules import MedicationScheduleUpdate

def get_schedules_for_medication(db: Session, medication_id: int) -> List[MedicationSchedule]:
    """Get all schedules for a given medication."""
    return db.query(MedicationSchedule).filter_by(medication_id=medication_id).all()


def create_medication_schedule(db: Session, medication_id: int, scheduled_time, dosage_instruction) -> MedicationSchedule:
    """Create a new medication schedule."""
    schedule = MedicationSchedule(
        medication_id=medication_id,
        scheduled_time=scheduled_time,
        dosage_instruction=dosage_instruction
    )
    db.add(schedule)
    db.flush()
    return schedule


def update_medication_schedule(db: Session, schedule_id: int, payload: MedicationScheduleUpdate) -> Optional[MedicationSchedule]:
    """Update an existing medication schedule."""
    schedule = db.query(MedicationSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        return None
    if payload.scheduled_time is not None:
        schedule.scheduled_time = payload.scheduled_time
    if payload.dosage_instruction is not None:
        schedule.dosage_instruction = payload.dosage_instruction
    return schedule


def delete_medication_schedule(db: Session, schedule_id: int) -> bool:
    """Delete a medication schedule."""
    schedule = db.query(MedicationSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        return False
    db.delete(schedule)
    return True
