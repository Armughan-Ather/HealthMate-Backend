from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from middlewares.auth import get_current_user
from utilities.permissions import can_modify_patient_logs
from crud.adhoc_bp_logs import create_adhoc_bp_log, get_adhoc_logs_by_patient, get_adhoc_bp_log
from schemas.adhoc_bp_logs import AdhocBPLogCreate, AdhocBPLogResponse

router = APIRouter()

@router.post("/patients/{patient_profile_id}/adhoc-bp-logs", response_model=AdhocBPLogResponse)
def create_log(patient_profile_id: int, data: AdhocBPLogCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Ensure patient_profile_id matches request body
    if data.patient_profile_id != patient_profile_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="patient_profile_id mismatch")

    if not can_modify_patient_logs(db, current_user, patient_profile_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add logs for this patient")

    return create_adhoc_bp_log(db, data)

@router.get("/patients/{patient_profile_id}/adhoc-bp-logs", response_model=List[AdhocBPLogResponse])
def list_logs(patient_profile_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not can_modify_patient_logs(db, current_user, patient_profile_id):
        # allow read for patient and attendants? we'll use same rule for now; change if needed
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view logs for this patient")
    return get_adhoc_logs_by_patient(db, patient_profile_id)

@router.get("/patients/{patient_profile_id}/adhoc-bp-logs/{log_id}", response_model=AdhocBPLogResponse)
def get_log(patient_profile_id: int, log_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    log = get_adhoc_bp_log(db, log_id)
    if not log or log.patient_profile_id != patient_profile_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    if not can_modify_patient_logs(db, current_user, patient_profile_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this log")
    return log
