from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from middlewares.auth import get_current_user
from crud import connections as connections_crud
from schemas.connections import (
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionResponse,
    ConnectionStatusEnum,
    ConnectionTypeEnum
)
from constants.enums import ConnectionTypeEnum as ModelConnectionType
from utilities.permissions import is_doctor, is_attendant, is_patient


router = APIRouter()

@router.post("/connections/", response_model=ConnectionResponse)
def create_connection(
    connection: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Allow either the patient or the connected_user to initiate a connection request
    if current_user.id not in (connection.patient_id, connection.connected_user_id):
        raise HTTPException(status_code=403, detail="Only the patient or the provider may initiate connection requests")

    # Validate connected_user role in DB to match requested connection_type
    # fetch connected user roles
    from models.user_roles import UserRole
    roles = db.query(UserRole).filter(UserRole.user_id == connection.connected_user_id).all()
    role_names = {r.role.value if hasattr(r.role, 'value') else str(r.role) for r in roles}

    if connection.connection_type == ConnectionTypeEnum.DOCTOR and 'DOCTOR' not in role_names:
        raise HTTPException(status_code=400, detail="Connected user is not a doctor")
    if connection.connection_type == ConnectionTypeEnum.ATTENDANT and 'ATTENDANT' not in role_names:
        raise HTTPException(status_code=400, detail="Connected user is not an attendant")

    return connections_crud.create_connection(db, connection)


@router.post("/connections/{connection_id}/cancel")
def cancel_connection_request(connection_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Patient can cancel a pending request they initiated
    conn = connections_crud.get_connection(db, connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    # either side that is part of this connection may cancel a pending request
    if current_user.id not in (conn.patient_id, conn.connected_user_id):
        raise HTTPException(status_code=403, detail="Not authorized to cancel this request")
    if conn.status != ConnectionStatusEnum.PENDING:
        raise HTTPException(status_code=400, detail="Only pending requests can be canceled")
    # mark as REVOKED to indicate cancellation
    from schemas.connections import ConnectionUpdate
    upd = ConnectionUpdate(status=ConnectionStatusEnum.REVOKED)
    return connections_crud.update_connection_status(db, connection_id, upd)


@router.post("/connections/{connection_id}/revoke")
def revoke_connection(connection_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Patient can revoke an accepted connection
    conn = connections_crud.get_connection(db, connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    if conn.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to revoke this connection")
    # only accepted connections can be revoked
    if conn.status != ConnectionStatusEnum.ACCEPTED:
        raise HTTPException(status_code=400, detail="Only accepted connections can be revoked")
    from schemas.connections import ConnectionUpdate
    upd = ConnectionUpdate(status=ConnectionStatusEnum.REVOKED)
    return connections_crud.update_connection_status(db, connection_id, upd)


@router.get("/connections/incoming", response_model=List[ConnectionResponse])
def incoming_requests(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Providers can list incoming pending requests where they are the connected_user
    return connections_crud.get_provider_connections(db, current_user.id, ConnectionStatusEnum.PENDING)

@router.get("/connections/patient/{patient_id}", response_model=List[ConnectionResponse])
def read_patient_connections(
    patient_id: int,
    status: Optional[ConnectionStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # patients can only view their own connections
    if current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these connections")
    return connections_crud.get_patient_connections(
        db, patient_id, status, skip, limit
    )

@router.get("/connections/provider/{provider_id}", response_model=List[ConnectionResponse])
def read_provider_connections(
    provider_id: int,
    status: Optional[ConnectionStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # providers (doctors/attendants) can only view connections where they are the connected_user
    if current_user.id != provider_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these connections")
    return connections_crud.get_provider_connections(
        db, provider_id, status, skip, limit
    )

@router.put("/connections/{connection_id}", response_model=ConnectionResponse)
def update_connection(
    connection_id: int,
    connection: ConnectionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_connection = connections_crud.get_connection(db, connection_id)
    if not db_connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    # Only the connected_user can accept/reject a connection
    if current_user.id != db_connection.connected_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this connection")

    # Only allow Accept or Reject via this endpoint
    if connection.status not in {ConnectionStatusEnum.ACCEPTED, ConnectionStatusEnum.REJECTED}:
        raise HTTPException(status_code=400, detail="Connected user may only accept or reject requests")

    return connections_crud.update_connection_status(db, connection_id, connection)