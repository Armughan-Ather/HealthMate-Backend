from sqlalchemy.orm import Session
from typing import List, Optional
from models.medicines import Medicine


def get_medicine_by_medicine_id(db: Session, medicine_id: int) -> Optional[Medicine]:
    """Get a specific medicine by ID."""
    return db.query(Medicine).filter_by(id=medicine_id).first()

def get_medicine_by_name_and_strength(db: Session, name: str, strength: str) -> Optional[Medicine]:
    """Get a specific medicine by its name and strength."""
    return db.query(Medicine).filter_by(name=name, strength=strength).first()

def get_medicine_by_name_strength_form(db: Session, name: str, strength: str, form: str) -> Optional[Medicine]:
    """Get a specific medicine by its name, strength and form."""
    return db.query(Medicine).filter_by(name=name, strength=strength, form=form).first()


def get_medicines(db: Session) -> List[Medicine]:
    """Get all medicines."""
    return db.query(Medicine).all()


def create_medicine(db: Session, name: str, strength: str, form: str, generic_name: Optional[str] = None) -> Medicine:
    """Create a new medicine or return an existing one."""
    existing = get_medicine_by_name_strength_form(db, name, strength, form)
    if existing:
        return existing
    medicine = Medicine(name=name, strength=strength, form=form, generic_name=generic_name)
    db.add(medicine)
    db.flush()
    return medicine