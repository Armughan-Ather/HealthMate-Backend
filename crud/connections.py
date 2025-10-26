from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models.connections import Connection
from constants.enums import ConnectionStatusEnum, ConnectionTypeEnum, UserRoleEnum
from schemas.connections import ConnectionCreate, ConnectionUpdate


def create_connection(
    db: Session,
    payload: ConnectionCreate,
    current_user_id: int,
    patient_id: int,
    connected_user_id: int
) -> Connection:
    """
    Create a new connection record. Handles role-based pairing and duplicate prevention.
    """
    existing = db.query(Connection).filter(
        Connection.patient_id == patient_id,
        Connection.connected_user_id == connected_user_id,
        Connection.connection_type == payload.connection_type,
        Connection.status.in_([ConnectionStatusEnum.PENDING, ConnectionStatusEnum.ACCEPTED])
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending or accepted connection between these users already exists."
        )

    conn = Connection(
        patient_id=patient_id,
        connected_user_id=connected_user_id,
        created_by_id=current_user_id,
        connection_type=payload.connection_type,
        status=ConnectionStatusEnum.PENDING
    )

    db.add(conn)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create connection (constraint violation: {str(exc.orig)})"
        )
    db.refresh(conn)
    return conn


# def get_connection(db: Session, connection_id: int, user_id: int, active_role: UserRoleEnum) -> Optional[Connection]:
#     if active_role == "PATIENT":
#         return db.query(Connection).filter(Connection.patient_id == user_id)
#     else:
#         return db.query(Connection).filter(Connection.connected_user_id == user_id, Connection.connection_type.name == active_role)
def get_connection(
    db: Session,
    connection_id: int,
    user_id: int,
    active_role: UserRoleEnum
) -> Optional[Connection]:
    query = db.query(Connection).filter(Connection.id == connection_id)

    if active_role == "PATIENT":
        query = query.filter(Connection.patient_id == user_id)
    else:
        query = query.filter(
            Connection.connected_user_id == user_id,
            Connection.connection_type == active_role  # compare directly to Enum
        )

    return query.first()


def update_connection_status(db: Session, connection_id: int, payload: ConnectionUpdate, user_id: int, active_role: UserRoleEnum) -> Connection:
    """
    Enforces strict state transitions with authorization checks.
    """
    conn = get_connection(db, connection_id, user_id, active_role)
    if not conn:
        raise HTTPException(404, "Connection not found")

    if user_id not in {conn.patient_id, conn.connected_user_id}:
        raise HTTPException(403, "Not authorized to update this connection")

    is_initiator = conn.created_by_id == user_id
    is_receiver = not is_initiator
    new_status = payload.status

    if conn.status == ConnectionStatusEnum.PENDING:
        if new_status == ConnectionStatusEnum.ACCEPTED and is_receiver:
            conn.status = new_status
        elif new_status == ConnectionStatusEnum.REJECTED and is_receiver:
            conn.status = new_status
        elif new_status == ConnectionStatusEnum.REVOKED and is_initiator:
            conn.status = new_status
        else:
            raise HTTPException(403, "Not authorized for this transition")

    elif conn.status == ConnectionStatusEnum.ACCEPTED:
        if new_status == ConnectionStatusEnum.REVOKED:
            conn.status = new_status
        else:
            raise HTTPException(400, "Invalid or unauthorized transition")

    else:
        raise HTTPException(400, f"Cannot update connection in {conn.status.value} state")

    db.commit()
    db.refresh(conn)
    return conn


def get_approved_connections_for_user(db: Session, user_id: int, active_role: str) -> List[Connection]:
    """Return accepted connections visible to this user’s current role context."""
    if active_role == "PATIENT":
        return db.query(Connection).filter(Connection.status == ConnectionStatusEnum.ACCEPTED, Connection.patient_id == user_id)
    else:
        return db.query(Connection).filter(Connection.status == ConnectionStatusEnum.ACCEPTED, Connection.connected_user_id == user_id, Connection.connection_type.name == active_role)


def get_pending_received(db: Session, user_id: int, active_role: str) -> List[Connection]:
    if active_role == "PATIENT":
        return db.query(Connection).filter(Connection.status == ConnectionStatusEnum.PENDING, Connection.patient_id == user_id, Connection.created_by_id != user_id)
    else:
        return db.query(Connection).filter(Connection.status == ConnectionStatusEnum.PENDING, Connection.connected_user_id == user_id, Connection.created_by_id != user_id, Connection.connection_type.name == active_role)


def get_pending_sent(db: Session, user_id: int, active_role: str) -> List[Connection]:
    if active_role == "PATIENT":
        return db.query(Connection).filter(Connection.status == ConnectionStatusEnum.PENDING, Connection.patient_id == user_id, Connection.created_by_id == user_id)
    else:
        return db.query(Connection).filter(Connection.status == ConnectionStatusEnum.PENDING, Connection.connected_user_id == user_id, Connection.created_by_id == user_id, Connection.connection_type.name == active_role)
