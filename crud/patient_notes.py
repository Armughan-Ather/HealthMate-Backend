from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models.patient_notes import PatientNote
from schemas.patient_notes import PatientNoteCreate, PatientNoteUpdate

def create_note(db: Session, note: PatientNoteCreate) -> PatientNote:
    db_note = PatientNote(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_note(db: Session, note_id: int) -> Optional[PatientNote]:
    return db.query(PatientNote).filter(PatientNote.id == note_id).first()

def get_user_notes(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    discussed_only: bool = False
) -> List[PatientNote]:
    query = db.query(PatientNote).filter(PatientNote.user_id == user_id)
    if discussed_only:
        query = query.filter(PatientNote.is_discussed == True)
    return query.order_by(PatientNote.created_at.desc()).offset(skip).limit(limit).all()

def update_note(
    db: Session,
    note_id: int,
    note: PatientNoteUpdate
) -> Optional[PatientNote]:
    db_note = get_note(db, note_id)
    if db_note:
        update_data = note.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_note, field, value)
        db_note.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int) -> bool:
    db_note = get_note(db, note_id)
    if db_note:
        db.delete(db_note)
        db.commit()
        return True
    return False