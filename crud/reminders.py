from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.reminders import Reminder
from app.schemas.reminders import ReminderCreate, ReminderUpdate

def create_reminder(db: Session, reminder: ReminderCreate) -> Reminder:
    db_reminder = Reminder(**reminder.model_dump())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def get_reminder(db: Session, reminder_id: int) -> Optional[Reminder]:
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()

def get_user_reminders(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> List[Reminder]:
    query = db.query(Reminder).filter(Reminder.user_id == user_id)
    if active_only:
        query = query.filter(Reminder.is_active == True)
    return query.order_by(Reminder.created_at.desc()).offset(skip).limit(limit).all()

def update_reminder(
    db: Session,
    reminder_id: int,
    reminder: ReminderUpdate
) -> Optional[Reminder]:
    db_reminder = get_reminder(db, reminder_id)
    if db_reminder:
        update_data = reminder.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_reminder, field, value)
        db_reminder.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_reminder)
    return db_reminder

def delete_reminder(db: Session, reminder_id: int) -> bool:
    db_reminder = get_reminder(db, reminder_id)
    if db_reminder:
        db.delete(db_reminder)
        db.commit()
        return True
    return False