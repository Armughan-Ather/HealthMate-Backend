from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_db, get_current_user
from app.crud import weights as weights_crud
from app.schemas.weights import WeightCreate, WeightUpdate, WeightResponse

router = APIRouter()

@router.post("/weights/", response_model=WeightResponse)
def create_weight(
    weight: WeightCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Verify if the current user is the patient or has permission
    if current_user.id != weight.patient_id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to create weight records for this patient"
        )
    return weights_crud.create_weight(db, weight)

@router.get("/patients/{patient_id}/weights/", response_model=List[WeightResponse])
def read_patient_weights(
    patient_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Add permission check here
    return weights_crud.get_patient_weights(db, patient_id, skip, limit)

@router.put("/weights/{weight_id}", response_model=WeightResponse)
def update_weight(
    weight_id: int,
    weight: WeightUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_weight = weights_crud.get_weight(db, weight_id)
    if not db_weight:
        raise HTTPException(status_code=404, detail="Weight record not found")
    if db_weight.patient_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to modify this weight record"
        )
    return weights_crud.update_weight(db, weight_id, weight)

@router.delete("/weights/{weight_id}")
def delete_weight(
    weight_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_weight = weights_crud.get_weight(db, weight_id)
    if not db_weight:
        raise HTTPException(status_code=404, detail="Weight record not found")
    if db_weight.patient_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to delete this weight record"
        )
    if weights_crud.delete_weight(db, weight_id):
        return {"message": "Weight record deleted successfully"}
    raise HTTPException(status_code=400, detail="Failed to delete weight record")