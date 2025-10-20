from sqlalchemy.orm import Session
from models.adhoc_bp_logs import AdhocBPLog
from schemas.adhoc_bp_logs import AdhocBPLogCreate
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


def create_adhoc_bp_log(db: Session, data: AdhocBPLogCreate) -> AdhocBPLog:
    log = AdhocBPLog(
        patient_profile_id=data.patient_profile_id,
        systolic=data.systolic,
        diastolic=data.diastolic,
        pulse=data.pulse,
        notes=data.notes,
        checked_at=data.checked_at
    )
    try:
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))


def get_adhoc_bp_log(db: Session, log_id: int) -> Optional[AdhocBPLog]:
    return db.query(AdhocBPLog).filter(AdhocBPLog.id == log_id).first()


def get_adhoc_logs_by_patient(db: Session, patient_profile_id: int) -> List[AdhocBPLog]:
    return db.query(AdhocBPLog).filter(AdhocBPLog.patient_profile_id == patient_profile_id).order_by(AdhocBPLog.checked_at.desc()).all()
