from sqlalchemy.orm import Session, joinedload
from models.adhoc_medication_logs import AdhocMedicationLog
from models.medicines import Medicine
from models.patient_profiles import PatientProfile
from schemas.adhoc_medication_logs import AdhocMedicationLogUpdate
from datetime import datetime, date
from typing import List
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from utilities.permissions import can_modify_patient_logs

def create_log(db: Session, log_data, actor_user) -> AdhocMedicationLog:
    if not can_modify_patient_logs(db, actor_user, log_data.patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized to create log for this patient")

    log = AdhocMedicationLog(
        patient_profile_id=log_data.patient_profile_id,
        medicine_id=log_data.medicine_id,
        dosage_taken=log_data.dosage_taken,
        notes=log_data.notes,
        taken_at=log_data.taken_at,
        logged_by=getattr(actor_user, 'id', None)
    )
    db.add(log)
    try:
        db.commit()
        db.refresh(log)
        return log
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create adhoc medication log due to a database constraint.",
        )

def get_log_if_owned(db: Session, log_id: int, actor_user):
    log = (
        db.query(AdhocMedicationLog)
        .options(
            joinedload(AdhocMedicationLog.medicine),
            joinedload(AdhocMedicationLog.patient)
        )
        .filter(AdhocMedicationLog.id == log_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    if not can_modify_patient_logs(db, actor_user, log.patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return log

def get_logs_by_patient_profile(db: Session, actor_user, patient_profile_id: int) -> List[AdhocMedicationLog]:
    if not can_modify_patient_logs(db, actor_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return (
        db.query(AdhocMedicationLog)
        .options(
            joinedload(AdhocMedicationLog.medicine),
            joinedload(AdhocMedicationLog.patient)
        )
        .filter(AdhocMedicationLog.patient_profile_id == patient_profile_id)
        .order_by(AdhocMedicationLog.taken_at.desc())
        .all()
    )

def get_logs_by_medicine(db: Session, actor_user, patient_profile_id: int, medicine_id: int) -> List[AdhocMedicationLog]:
    if not can_modify_patient_logs(db, actor_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return (
        db.query(AdhocMedicationLog)
        .options(
            joinedload(AdhocMedicationLog.medicine),
            joinedload(AdhocMedicationLog.patient)
        )
        .filter(
            AdhocMedicationLog.patient_profile_id == patient_profile_id,
            AdhocMedicationLog.medicine_id == medicine_id
        )
        .order_by(AdhocMedicationLog.taken_at.desc())
        .all()
    )

def update_log(db: Session, log_id: int, updates: AdhocMedicationLogUpdate, actor_user):
    log = get_log_if_owned(db, log_id, actor_user)
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log

def delete_log(db: Session, log_id: int, actor_user):
    log = get_log_if_owned(db, log_id, actor_user)
    db.delete(log)
    db.commit()
    return True

def get_logs_by_date(db: Session, actor_user, patient_profile_id: int, target_date: date) -> List[AdhocMedicationLog]:
    if not can_modify_patient_logs(db, actor_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return (
        db.query(AdhocMedicationLog)
        .options(
            joinedload(AdhocMedicationLog.medicine),
            joinedload(AdhocMedicationLog.patient)
        )
        .filter(
            AdhocMedicationLog.patient_profile_id == patient_profile_id,
            AdhocMedicationLog.taken_at.cast(date) == target_date
        )
        .order_by(AdhocMedicationLog.taken_at.desc())
        .all()
    )

def get_logs_by_date_range(db: Session, actor_user, patient_profile_id: int, start_date: date, end_date: date) -> List[AdhocMedicationLog]:
    if not can_modify_patient_logs(db, actor_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return (
        db.query(AdhocMedicationLog)
        .options(
            joinedload(AdhocMedicationLog.medicine),
            joinedload(AdhocMedicationLog.patient)
        )
        .filter(
            AdhocMedicationLog.patient_profile_id == patient_profile_id,
            AdhocMedicationLog.taken_at.between(
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date, datetime.max.time())
            )
        )
        .order_by(AdhocMedicationLog.taken_at.desc())
        .all()
    )

def get_logs_by_user(db: Session, actor_user):
    # Return logs for patients where the actor can modify logs
    return (
        db.query(AdhocMedicationLog)
        .options(
            joinedload(AdhocMedicationLog.medicine),
            joinedload(AdhocMedicationLog.patient)
        )
        .filter(AdhocMedicationLog.logged_by == getattr(actor_user, 'id', None))
        .order_by(AdhocMedicationLog.taken_at.desc())
        .all()
    )
