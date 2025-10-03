from sqlalchemy import (
    Column, Integer, Text, 
    DateTime, ForeignKey, CheckConstraint, JSON, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), nullable=False, index=True)
    request = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(request)) >= 1", name='check_message_request_not_empty'),
        CheckConstraint("LENGTH(TRIM(response)) >= 1", name='check_message_response_not_empty'),
        CheckConstraint("LENGTH(request) <= 50000", name='check_message_request_max_length'),
        CheckConstraint("LENGTH(response) <= 100000", name='check_message_response_max_length'),
        Index('idx_message_chat_created', 'chat_id', 'created_at'),
    )