from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class MessagePair(BaseModel):
    user: str
    ai: str


class MessageCreate(BaseModel):
    chat_id: Optional[int] = None
    request: str
    metadata: Optional[Any] = None


class Regenerate_Message(BaseModel):
    chat_id: int


class MessageResponse(BaseModel):
    id: int
    chat_id: Optional[int] = None
    request: str
    response: str
    metadata: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
