from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from middlewares.auth import get_current_user
from models.users import User
from crud import medications as medications_crud
from schemas.medications import (
    MedicationCreateWithSchedules,
    MedicationResponse,
    MedicationUpdate
)
from utilities.permissions import can_modify_patient_schedules

router = APIRouter()


@router.post("/patients/{patient_profile_id}/medications", response_model=MedicationResponse, status_code=201)
def create_medication_for_patient(
    patient_profile_id: int,
    payload: MedicationCreateWithSchedules,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # RBAC: patient, attendant, or connected doctor may create medications
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to create medication for this patient")
    med = medications_crud.create_medication_with_schedules(db, patient_profile_id, current_user.id, payload)
    db.commit()
    db.refresh(med)
    return med


@router.get("/patients/{patient_profile_id}/medications", response_model=List[MedicationResponse])
def list_medications_for_patient(patient_profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not can_modify_patient_schedules(db, current_user, patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view medications for this patient")
    return medications_crud.get_user_medications(db, patient_profile_id)


@router.get("/medications/{medication_id}", response_model=MedicationResponse)
def get_medication(medication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    med = db.query(medications_crud.Medication).filter_by(id=medication_id).first()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    if not can_modify_patient_schedules(db, current_user, med.patient_profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this medication")
    return med


@router.put("/medications/{medication_id}", response_model=MedicationResponse)
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


@router.delete("/medications/{medication_id}")
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
# from typing import List, Dict
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from database import get_db
# from middlewares.auth import get_current_user
# from crud.medications import (
#     create_medication_with_schedules,
#     get_user_medications,
#     update_medication,
#     delete_medication,
#     count_medications
# )
# from schemas.medications import (
#     MedicationCreateWithSchedules,
#     MedicationResponse,
#     MedicationUpdate
# )
# from models.users import User

# router = APIRouter()


# @router.post("", response_model=MedicationResponse, status_code=201)
# def create_new_medication(payload: MedicationCreateWithSchedules, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """Create a new medication along with its schedules for the current user."""
#     medication = create_medication_with_schedules(db, current_user.id, payload)
#     db.commit()
#     db.refresh(medication)
#     return medication


# @router.get("/count", response_model=Dict[str, int])
# def count_user_medications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     """Count active medications for the current user."""
#     active_count = count_medications(db, current_user.id)
#     return {"active_count": active_count}


# @router.get("", response_model=List[MedicationResponse])
# def list_user_medications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     """List all medications for the current user."""
#     medications = get_user_medications(db, current_user.id)
#     return medications


# @router.put("/{medication_id}", response_model=MedicationResponse)
# def update_user_medication(medication_id: int, payload: MedicationUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     """Update an existing medication."""
#     medication = update_medication(db, medication_id, payload)
#     if not medication or medication.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Medication not found.")
#     db.commit()
#     db.refresh(medication)
#     return medication


# @router.delete("/{medication_id}", status_code=204)
# def delete_user_medication(medication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """Delete an existing medication."""
#     deleted = delete_medication(db, medication_id, current_user.id)
#     if not deleted:
#         raise HTTPException(status_code=404, detail="Medication not found.")
#     db.commit()
#     return