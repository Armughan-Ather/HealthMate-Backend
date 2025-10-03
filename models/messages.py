from sqlalchemy import (
    Column, Integer, Text, 
    DateTime, ForeignKey, CheckConstraint, JSON, Index
)
from sqlalchemy.orm import relationship, validates
import json
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

    @validates('request')
    def validate_request(self, key, value):
        if not value or not value.strip():
            raise ValueError("Request cannot be empty")
        trimmed = value.strip()
        if len(trimmed) > 50000:
            raise ValueError("Request exceeds maximum length of 50,000 characters")
        return trimmed

    @validates('response')
    def validate_response(self, key, value):
        if not value or not value.strip():
            raise ValueError("Response cannot be empty")
        trimmed = value.strip()
        if len(trimmed) > 100000:
            raise ValueError("Response exceeds maximum length of 100,000 characters")
        return trimmed

    @validates('metadata')
    def validate_metadata(self, key, value):
        if value is None:
            return value
        # Optional: ensure metadata is JSON-serializable
        try:
            json.dumps(value)
        except (TypeError, ValueError):
            raise ValueError("Metadata must be a valid JSON object")
        if not isinstance(value, (dict, list)):
            raise ValueError("Metadata must be a dictionary or list")
        return value