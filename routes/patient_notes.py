from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from middlewares.auth import get_current_user
from database import get_db
from crud import patient_notes as notes_crud
from schemas.patient_notes import (
    PatientNoteCreate,
    PatientNoteUpdate,
    PatientNoteResponse
)

router = APIRouter()

@router.post("/patient-notes/", response_model=PatientNoteResponse)
def create_note(
    note: PatientNoteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.id != note.user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create notes for other users"
        )
    return notes_crud.create_note(db, note)

@router.get("/patient-notes/", response_model=List[PatientNoteResponse])
def read_notes(
    skip: int = 0,
    limit: int = 100,
    discussed_only: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return notes_crud.get_user_notes(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
        discussed_only=discussed_only
    )

@router.get("/patient-notes/{note_id}", response_model=PatientNoteResponse)
def read_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    note = notes_crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this note")
    return note

@router.put("/patient-notes/{note_id}", response_model=PatientNoteResponse)
def update_note(
    note_id: int,
    note: PatientNoteUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_note = notes_crud.get_note(db, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    if db_note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this note")
    return notes_crud.update_note(db, note_id, note)

@router.delete("/patient-notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_note = notes_crud.get_note(db, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    if db_note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")
    if notes_crud.delete_note(db, note_id):
        return {"message": "Note deleted successfully"}
    raise HTTPException(status_code=400, detail="Failed to delete note")