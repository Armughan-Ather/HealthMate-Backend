from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from constants.enums import ConnectionTypeEnum, ConnectionStatusEnum


class ConnectionBase(BaseModel):
    connection_type: ConnectionTypeEnum


class ConnectionCreate(ConnectionBase):
    target_user_id: int


class ConnectionUpdate(BaseModel):
    status: ConnectionStatusEnum


class ConnectionResponse(BaseModel):
    id: int
    patient_id: int
    connected_user_id: int
    created_by_id: int
    connection_type: ConnectionTypeEnum
    status: ConnectionStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
