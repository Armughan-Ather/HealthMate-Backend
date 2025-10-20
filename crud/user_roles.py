from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models.user_roles import UserRole
from schemas.user_roles import UserRoleCreate
from sqlalchemy.exc import IntegrityError


def create_user_role(db: Session, role: UserRoleCreate) -> UserRole:
    db_role = UserRole(**role.model_dump())
    db.add(db_role)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(db_role)
    return db_role


def get_user_role(db: Session, role_id: int) -> Optional[UserRole]:
    return db.query(UserRole).filter(UserRole.id == role_id).first()


def get_roles_for_user(db: Session, user_id: int) -> List[UserRole]:
    return db.query(UserRole).filter(UserRole.user_id == user_id).all()


def delete_user_role(db: Session, role_id: int) -> bool:
    db_role = get_user_role(db, role_id)
    if db_role:
        db.delete(db_role)
        db.commit()
        return True
    return False