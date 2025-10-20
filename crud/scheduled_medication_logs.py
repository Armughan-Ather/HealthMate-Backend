from sqlalchemy.orm import Session, joinedload
from models.scheduled_medication_logs import ScheduledMedicationLog
from models.medication_schedules import MedicationSchedule
from models.medications import Medication
from schemas.scheduled_medication_logs import MedicationLogUpdate
from datetime import datetime, date
from typing import List
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from utilities.permissions import can_modify_patient_logs, can_modify_patient_schedules

def create_log(db: Session, schedule_id: int, log_data, actor_user: int) -> ScheduledMedicationLog:
    schedule = (
        db.query(MedicationSchedule)
        .options(joinedload(MedicationSchedule.medication))
        .filter(MedicationSchedule.id == schedule_id)
        .first()
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Medication schedule not found")
    medication = schedule.medication
    if not can_modify_patient_logs(db, actor_user, medication.patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized to create log for this medication")

    log = ScheduledMedicationLog(
        medication_schedule_id=schedule_id,
        taken_at=log_data.taken_at,
        notes=log_data.notes,
        logged_by=actor_user
    )
    db.add(log)
    try:
        db.commit()
        db.refresh(log)
        return log
    except IntegrityError as e:
        db.rollback()
        if 'medication_schedule_id' in str(e.orig) and 'scheduled_date' in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A log for this schedule and date already exists.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create medication log due to a database constraint.",
        )


def get_log_if_owned(db: Session, log_id: int, actor_user):
    log = (
        db.query(ScheduledMedicationLog)
        .options(
            joinedload(ScheduledMedicationLog.schedule)
            .joinedload(MedicationSchedule.medication)
            .joinedload(Medication.medicine)
        )
        .filter(ScheduledMedicationLog.id == log_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    medication = log.schedule.medication
    if not can_modify_patient_schedules(db, actor_user, medication.patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return log


def get_logs_by_schedule_id(db: Session, schedule_id: int, actor_user) -> List[ScheduledMedicationLog]:
    schedule = db.query(MedicationSchedule).filter(MedicationSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Medication schedule not found")
    medication = schedule.medication
    if not can_modify_patient_schedules(db, actor_user, medication.patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return (
        db.query(ScheduledMedicationLog)
        .options(
            joinedload(ScheduledMedicationLog.schedule)
            .joinedload(MedicationSchedule.medication)
            .joinedload(Medication.medicine)
        )
        .filter(ScheduledMedicationLog.medication_schedule_id == schedule_id)
        .all()
    )


def update_log(db: Session, log_id: int, updates: MedicationLogUpdate, actor_user):
    log = (
        db.query(ScheduledMedicationLog)
        .options(
            joinedload(ScheduledMedicationLog.schedule)
            .joinedload(MedicationSchedule.medication)
            .joinedload(Medication.medicine)
        )
        .filter(ScheduledMedicationLog.id == log_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    medication = log.schedule.medication
    if not can_modify_patient_logs(db, actor_user, medication.patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log

def delete_log(db: Session, log_id: int, actor_user):
    log = (
        db.query(ScheduledMedicationLog)
        .options(
            joinedload(ScheduledMedicationLog.schedule)
            .joinedload(MedicationSchedule.medication)
            .joinedload(Medication.medicine)
        )
        .filter(ScheduledMedicationLog.id == log_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    medication = log.schedule.medication
    if not can_modify_patient_logs(db, actor_user, medication.patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    db.delete(log)
    db.commit()
    return True


def get_logs_by_date(db: Session, user_id: int, target_date: date, patient_profile_id: int):
    if not can_modify_patient_logs(db, user_id, patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return (
        db.query(ScheduledMedicationLog)
        .join(ScheduledMedicationLog.schedule)
        .join(MedicationSchedule.medication)
        .filter(
            ScheduledMedicationLog.taken_at.cast(date) == target_date,
            MedicationSchedule.medication.has(patient_profile_id=patient_profile_id)
        )
        .options(
            joinedload(ScheduledMedicationLog.schedule)
            .joinedload(MedicationSchedule.medication)
            .joinedload(Medication.medicine)
        )
        .all()
    )

def get_logs_by_date_range(db: Session, user_id, patient_profile_id: int, start_date: date, end_date: date):
    if not can_modify_patient_logs(db, user_id, patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return (
        db.query(ScheduledMedicationLog)
        .join(ScheduledMedicationLog.schedule)
        .join(MedicationSchedule.medication)
        .filter(
            ScheduledMedicationLog.taken_at.between(datetime.combine(start_date, datetime.min.time()),
                                                        datetime.combine(end_date, datetime.max.time())),
            MedicationSchedule.medication.has(patient_profile_id=patient_profile_id)
            )
        .options(
            joinedload(ScheduledMedicationLog.schedule)
            .joinedload(MedicationSchedule.medication)
            .joinedload(Medication.medicine)
        )
        .all()
    )

def get_logs_by_medicine(db: Session, user_id: int, patient_profile_id: int, medicine_id: int):
    if not can_modify_patient_logs(db, user_id, patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return (
        db.query(ScheduledMedicationLog)
        .join(ScheduledMedicationLog.schedule)
        .join(MedicationSchedule.medication)
        .filter(
            MedicationSchedule.medication.has(patient_profile_id=patient_profile_id, medicine_id=medicine_id)
        )
        .options(
            joinedload(ScheduledMedicationLog.schedule)
            .joinedload(MedicationSchedule.medication)
            .joinedload(Medication.medicine)
        )
        .all()
    )

def get_logs_by_user(db: Session, actor_user):
    # Return logs for medications where the actor can modify logs. This needs filtering in routes or a join to connections; for now, return own logs (logged_by)
    return (
        db.query(ScheduledMedicationLog)
        .options(
            joinedload(ScheduledMedicationLog.schedule)
            .joinedload(MedicationSchedule.medication)
            .joinedload(Medication.medicine)
        )
        .filter(ScheduledMedicationLog.logged_by == getattr(actor_user, 'id', None))
        .all()
    )

def get_logs_by_user(db: Session, user_id: int, patient_profile_id: int):
    if not can_modify_patient_logs(db, user_id, patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return (
        db.query(ScheduledMedicationLog)
        .options(
            joinedload(ScheduledMedicationLog.schedule)
            .joinedload(MedicationSchedule.medication)
            .joinedload(Medication.medicine)
        )
        .filter(ScheduledMedicationLog.logged_by == user_id, MedicationSchedule.medication.has(patient_profile_id=patient_profile_id))
        .all()
    )