from sqlalchemy.orm import Session
from app.models.weights import Weight
from app.schemas.weights import WeightCreate, WeightUpdate
from typing import List, Optional
from datetime import datetime

def create_weight(db: Session, weight: WeightCreate) -> Weight:
    db_weight = Weight(**weight.model_dump())
    db.add(db_weight)
    db.commit()
    db.refresh(db_weight)
    return db_weight

def get_weight(db: Session, weight_id: int) -> Optional[Weight]:
    return db.query(Weight).filter(Weight.id == weight_id).first()

def get_patient_weights(
    db: Session, 
    patient_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Weight]:
    return db.query(Weight)\
        .filter(Weight.patient_id == patient_id)\
        .order_by(Weight.measured_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def update_weight(
    db: Session, 
    weight_id: int, 
    weight: WeightUpdate
) -> Optional[Weight]:
    db_weight = get_weight(db, weight_id)
    if db_weight:
        update_data = weight.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_weight, field, value)
        db_weight.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_weight)
    return db_weight

def delete_weight(db: Session, weight_id: int) -> bool:
    db_weight = get_weight(db, weight_id)
    if db_weight:
        db.delete(db_weight)
        db.commit()
        return True
    return False