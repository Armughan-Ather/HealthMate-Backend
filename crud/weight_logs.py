from sqlalchemy.orm import Session
from models.weight_logs import WeightLog
from schemas.weight_logs import WeightCreate, WeightUpdate
from typing import List, Optional
from datetime import datetime

def create_weight(db: Session, weight: WeightCreate) -> WeightLog:
    db_weight = WeightLog(**weight.model_dump())
    db.add(db_weight)
    db.commit()
    db.refresh(db_weight)
    return db_weight

def get_weight(db: Session, weight_id: int) -> Optional[WeightLog]:
    return db.query(WeightLog).filter(WeightLog.id == weight_id).first()

def get_patient_weights(
    db: Session, 
    patient_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[WeightLog]:
    return db.query(WeightLog)\
        .filter(WeightLog.patient_id == patient_id)\
        .order_by(WeightLog.measured_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def update_weight(
    db: Session, 
    weight_id: int, 
    weight: WeightUpdate
) -> Optional[WeightLog]:
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