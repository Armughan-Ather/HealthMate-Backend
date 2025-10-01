from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_db, get_current_user
from app.crud import connections as connections_crud
from app.schemas.connections import (
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionResponse,
    ConnectionStatusEnum
)

router = APIRouter()

@router.post("/connections/", response_model=ConnectionResponse)
def create_connection(
    connection: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Verify if current user is authorized to create this connection
    if current_user.id not in [connection.patient_id, connection.connected_user_id]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create this connection"
        )
    return connections_crud.create_connection(db, connection)

@router.get("/connections/patient/{patient_id}", response_model=List[ConnectionResponse])
def read_patient_connections(
    patient_id: int,
    status: Optional[ConnectionStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.id != patient_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view these connections"
        )
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
    if current_user.id != provider_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view these connections"
        )
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
    if current_user.id != db_connection.connected_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this connection"
        )
    return connections_crud.update_connection_status(db, connection_id, connection)