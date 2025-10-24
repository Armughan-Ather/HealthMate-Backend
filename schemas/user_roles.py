from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from constants.enums import UserRoleEnum

class SwitchRoleRequest(BaseModel):
    new_role: UserRoleEnum

class UserRoleBase(BaseModel):
    role: UserRoleEnum


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleResponse(UserRoleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True