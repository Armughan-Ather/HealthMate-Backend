from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from database import get_db
from middlewares.auth import get_current_user, require_medical_staff, require_patient, require_attendant, require_doctor
from models.users import User
from crud import medications as medications_crud
from schemas.medications import (
    MedicationCreateWithSchedules,
    MedicationResponse,
    MedicationUpdate
)
from utilities.permissions import can_modify_patient_schedules

router = APIRouter()

# 🩺 For doctors/attendants managing a patient
@router.post("/patients/{patient_profile_id}", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
def create_medication_for_patient(patient_profile_id: int, payload: MedicationCreateWithSchedules, db: Session = Depends(get_db), current_user: User = Depends(require_medical_staff)):
    """
    Create a medication for a specific patient.
    Accessible by attendants and connected doctors.
    """
    return medications_crud.create_medication_core(db, current_user, patient_profile_id, payload)


@router.get("/patients/{patient_profile_id}", response_model=List[MedicationResponse])
def list_medications_for_patient(patient_profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_medical_staff)):
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view medications for this patient")
    return medications_crud.get_user_medications(db, patient_profile_id)

@router.get("/count/{patient_profile_id}", response_model=Dict[str, int])
def count_user_medications(patient_profile_id:int, db: Session = Depends(get_db), current_user=Depends(require_medical_staff)):
    """Count active medications for the current user."""
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view medications for this patient")
    active_count = medications_crud.count_medications(db, patient_profile_id)
    return {"active_count": active_count}

@router.get("/{medication_id}", response_model=MedicationResponse)
def get_medication(medication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    med = db.query(medications_crud.Medication).filter_by(id=medication_id).first()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    if not can_modify_patient_schedules(db, current_user, med.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this medication")
    return med


@router.put("/{medication_id}", response_model=MedicationResponse)
def update_medication(medication_id: int, payload: MedicationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    med = db.query(medications_crud.Medication).filter_by(id=medication_id).first()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    if not can_modify_patient_schedules(db, current_user, med.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this medication")
    updated = medications_crud.update_medication(db, medication_id, payload)
    db.commit()
    db.refresh(updated)
    return updated


@router.delete("/{medication_id}")
def delete_medication(medication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    med = db.query(medications_crud.Medication).filter_by(id=medication_id).first()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    if not can_modify_patient_schedules(db, current_user, med.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this medication")
    success = medications_crud.delete_medication(db, medication_id, med.patient_profile_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete medication")
    db.commit()
    return {"message": "Medication deleted"}


@router.get("", response_model=List[MedicationResponse])
def list_user_medications(db: Session = Depends(get_db), current_user=Depends(require_patient)):
    """List all medications for the current user."""
    medications = medications_crud.get_user_medications(db, current_user.id)
    return medications


# 👤 For patients adding their own medication
@router.post("", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
def create_medication_for_self(payload: MedicationCreateWithSchedules, db: Session = Depends(get_db), current_user: User = Depends(require_patient)):
    """
    Create a medication for the current patient (self).
    Only accessible if the current user is a patient.
    """
    return medications_crud.create_medication_core(db, current_user, current_user.id, payload)


@router.get("/me/count", response_model=Dict[str, int])
def count_user_medications(db: Session = Depends(get_db), current_user=Depends(require_patient)):
    """Count active medications for the current user."""
    active_count = medications_crud.count_medications(db, current_user.id)
    return {"active_count": active_count}
