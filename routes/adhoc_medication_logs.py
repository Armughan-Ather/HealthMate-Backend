from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.adhoc_medication_logs import (
    AdhocMedicationLogCreate,
    AdhocMedicationLogUpdate,
    AdhocMedicationLogResponse
)
from crud.adhoc_medication_logs import (
    create_log,
    get_log_if_owned,
    get_logs_by_patient_profile,
    get_logs_by_medicine,
    update_log,
    delete_log,
    get_logs_by_date,
    get_logs_by_date_range,
    get_logs_by_user
)
from typing import List, Optional
from models import User
from middlewares.auth import get_current_user
from datetime import date

router = APIRouter()

@router.get("/logs/user", response_model=List[AdhocMedicationLogResponse])
def list_user_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_logs_by_user(db, current_user)

@router.post("/patients/{patient_profile_id}", response_model=AdhocMedicationLogResponse, status_code=status.HTTP_201_CREATED)
def create_adhoc_medication_log(
    patient_profile_id: int,
    payload: AdhocMedicationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Override patient_profile_id from path parameter
    payload.patient_profile_id = patient_profile_id
    return create_log(db, payload, current_user)

@router.get("/{log_id}", response_model=AdhocMedicationLogResponse)
def get_adhoc_medication_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_log_if_owned(db, log_id, current_user)

@router.get("/patients/{patient_profile_id}", response_model=List[AdhocMedicationLogResponse])
def get_logs_for_patient(
    patient_profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_logs_by_patient_profile(db, current_user, patient_profile_id)

@router.get("/patients/{patient_profile_id}/medicine/{medicine_id}", response_model=List[AdhocMedicationLogResponse])
def get_logs_by_medicine_for_patient(
    patient_profile_id: int,
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_logs_by_medicine(db, current_user, patient_profile_id, medicine_id)

@router.put("/{log_id}", response_model=AdhocMedicationLogResponse)
def update_adhoc_medication_log(
    log_id: int,
    payload: AdhocMedicationLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_log(db, log_id, payload, current_user)

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adhoc_medication_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_log(db, log_id, current_user)

@router.get("/patients/{patient_profile_id}/date", response_model=List[AdhocMedicationLogResponse])
def get_logs_by_date_or_range(
    patient_profile_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if date_from and date_to:
        logs = get_logs_by_date_range(db, current_user, patient_profile_id, date_from, date_to)
    elif date_from:
        logs = get_logs_by_date(db, current_user, patient_profile_id, date_from)
    else:
        raise HTTPException(status_code=400, detail="Please provide at least date_from or both date_from and date_to")
    return logs
