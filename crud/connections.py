from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.connections import Connection, ConnectionStatusEnum
from app.schemas.connections import ConnectionCreate, ConnectionUpdate

def create_connection(db: Session, connection: ConnectionCreate) -> Connection:
    db_connection = Connection(
        **connection.model_dump(),
        status=ConnectionStatusEnum.PENDING,
        requested_at=datetime.utcnow()
    )
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection

def get_connection(db: Session, connection_id: int) -> Optional[Connection]:
    return db.query(Connection).filter(Connection.id == connection_id).first()

def get_patient_connections(
    db: Session,
    patient_id: int,
    status: Optional[ConnectionStatusEnum] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Connection]:
    query = db.query(Connection).filter(Connection.patient_id == patient_id)
    if status:
        query = query.filter(Connection.status == status)
    return query.offset(skip).limit(limit).all()

def get_provider_connections(
    db: Session,
    provider_id: int,
    status: Optional[ConnectionStatusEnum] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Connection]:
    query = db.query(Connection).filter(Connection.connected_user_id == provider_id)
    if status:
        query = query.filter(Connection.status == status)
    return query.offset(skip).limit(limit).all()

def update_connection_status(
    db: Session,
    connection_id: int,
    connection_update: ConnectionUpdate
) -> Optional[Connection]:
    db_connection = get_connection(db, connection_id)
    if db_connection:
        update_data = connection_update.model_dump()
        for field, value in update_data.items():
            setattr(db_connection, field, value)
        db_connection.responded_at = datetime.utcnow()
        db.commit()
        db.refresh(db_connection)
    return db_connection