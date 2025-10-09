from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class ConnectionTypeEnum(str, Enum):
    DOCTOR = "DOCTOR"
    ATTENDANT = "ATTENDANT"


class ConnectionStatusEnum(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"


class ConnectionBase(BaseModel):
    patient_id: int
    connected_user_id: int
    connection_type: ConnectionTypeEnum
    request_message: Optional[str] = None


class ConnectionCreate(ConnectionBase):
    pass


class ConnectionUpdate(BaseModel):
    status: ConnectionStatusEnum


class ConnectionResponse(ConnectionBase):
    id: int
    status: ConnectionStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True