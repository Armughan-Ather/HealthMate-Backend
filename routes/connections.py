from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from middlewares.auth import get_current_user
from schemas.connections import ConnectionCreate, ConnectionUpdate, ConnectionResponse
from crud import connections as conn_crud
from models.user_roles import UserRole
from models.users import User
from constants.enums import ConnectionTypeEnum

router = APIRouter(prefix="/connections", tags=["Connections"])


@router.post("", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
def create_connection(
    payload: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new connection.
    - If user is a PATIENT, they connect to a DOCTOR or ATTENDANT.
    - If user is a DOCTOR or ATTENDANT, they connect to a PATIENT.
    - Each user’s active role context defines the scope of visibility.
    """

    # Fetch roles for initiator and target
    my_roles = {r.role.value for r in db.query(UserRole).filter(UserRole.user_id == current_user.id).all()}
    target_roles = {r.role.value for r in db.query(UserRole).filter(UserRole.user_id == payload.target_user_id).all()}

    # Role logic
    if current_user.active_role.value == "PATIENT":
        if "PATIENT" not in my_roles:
            raise HTTPException(status_code=400, detail="You are not a patient.")
        patient_id = current_user.id
        connected_user_id = payload.target_user_id

        if payload.connection_type == ConnectionTypeEnum.DOCTOR and "DOCTOR" not in target_roles:
            raise HTTPException(status_code=400, detail="Target user is not a doctor.")
        if payload.connection_type == ConnectionTypeEnum.ATTENDANT and "ATTENDANT" not in target_roles:
            raise HTTPException(status_code=400, detail="Target user is not an attendant.")

    elif current_user.active_role.value in ("DOCTOR", "ATTENDANT"):
        if current_user.active_role.value != payload.connection_type.name:
            raise HTTPException(
                status_code=400,
                detail=f"As a {current_user.active_role.value.lower()}, you can only create "
                       f"{current_user.active_role.value.lower()} connections."
            )
        if "PATIENT" not in target_roles:
            raise HTTPException(status_code=400, detail="Target user is not a patient.")

        patient_id = payload.target_user_id
        connected_user_id = current_user.id

    else:
        raise HTTPException(status_code=400, detail="User role not permitted to initiate connection.")

    # Create and trigger notifications
    connection = conn_crud.create_connection(
        db=db,
        payload=payload,
        current_user_id=current_user.id,
        patient_id=patient_id,
        connected_user_id=connected_user_id
    )

    return connection


@router.put("/{connection_id}", response_model=ConnectionResponse)
def update_connection_status(
    connection_id: int,
    payload: ConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve, reject, or revoke a connection based on user role and state transitions."""
    connection = conn_crud.update_connection_status(db, connection_id, payload, current_user.id, current_user.active_role.value)
    return connection


@router.get("", response_model=List[ConnectionResponse])
def get_approved_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return all accepted connections in current user’s active role context."""
    return conn_crud.get_approved_connections_for_user(db, current_user.id, current_user.active_role.value)


@router.get("/requests/received", response_model=List[ConnectionResponse])
def get_pending_received(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return all pending connection requests received by the user."""
    return conn_crud.get_pending_received(db, current_user.id, current_user.active_role.value)


@router.get("/requests/sent", response_model=List[ConnectionResponse])
def get_pending_sent(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return all pending connection requests sent by the user."""
    return conn_crud.get_pending_sent(db, current_user.id, current_user.active_role.value)
