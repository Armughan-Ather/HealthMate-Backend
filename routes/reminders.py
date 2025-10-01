from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_db, get_current_user
from app.crud import reminders as reminders_crud
from app.schemas.reminders import ReminderCreate, ReminderUpdate, ReminderResponse

router = APIRouter()

@router.post("/reminders/", response_model=ReminderResponse)
def create_reminder(
    reminder: ReminderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.id != reminder.user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create reminders for other users"
        )
    reminder.created_by = current_user.id
    return reminders_crud.create_reminder(db, reminder)

@router.get("/reminders/", response_model=List[ReminderResponse])
def read_reminders(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return reminders_crud.get_user_reminders(
        db, 
        current_user.id, 
        skip=skip, 
        limit=limit, 
        active_only=active_only
    )

@router.put("/reminders/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: int,
    reminder: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_reminder = reminders_crud.get_reminder(db, reminder_id)
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if db_reminder.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this reminder")
    return reminders_crud.update_reminder(db, reminder_id, reminder)

@router.delete("/reminders/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_reminder = reminders_crud.get_reminder(db, reminder_id)
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if db_reminder.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this reminder")
    if reminders_crud.delete_reminder(db, reminder_id):
        return {"message": "Reminder deleted successfully"}
    raise HTTPException(status_code=400, detail="Failed to delete reminder")