from sqlalchemy.orm import Session
from app.models.roles import Role
from app.schemas.roles import RoleCreate, RoleUpdate
from typing import List, Optional
from datetime import datetime

def create_role(db: Session, role: RoleCreate) -> Role:
    db_role = Role(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    return db.query(Role).offset(skip).limit(limit).all()

def update_role(db: Session, role_id: int, role: RoleUpdate) -> Optional[Role]:
    db_role = get_role(db, role_id)
    if db_role:
        update_data = role.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_role, field, value)
        db_role.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int) -> bool:
    db_role = get_role(db, role_id)
    if db_role:
        db.delete(db_role)
        db.commit()
        return True
    return False