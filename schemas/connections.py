from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class ConnectionType(str, Enum):
    DOCTOR = "doctor"
    CAREGIVER = "caregiver"
    FAMILY = "family"
    OTHER = "other"

class ConnectionBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    connection_type: ConnectionType
    notes: Optional[str] = None

class ConnectionCreate(ConnectionBase):
    pass

class ConnectionUpdate(ConnectionBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    connection_type: Optional[ConnectionType] = None

class ConnectionResponse(ConnectionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True