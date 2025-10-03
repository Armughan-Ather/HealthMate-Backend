from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from database import Base


class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    topic = Column(String(500), nullable=False)
    summary = Column(Text, default='', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(topic)) >= 3", name='check_chat_topic_min_length'),
        CheckConstraint("LENGTH(topic) <= 500", name='check_chat_topic_max_length'),
        CheckConstraint("LENGTH(summary) <= 2000", name='check_chat_summary_max_length'),
        Index('idx_chat_user_active', 'user_id', 'is_active'),
        Index('idx_chat_created_at', 'created_at'),
    )

    @validates('topic')
    def validate_topic(self, key, value):
        if not value or not value.strip():
            raise ValueError("Chat topic cannot be empty")
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Chat topic must be at least 3 characters long")
        if len(value) > 500:
            raise ValueError("Chat topic cannot exceed 500 characters")
        return value

    @validates('summary')
    def validate_summary(self, key, value):
        if value is None:
            return ''
        if len(value) > 2000:
            raise ValueError("Chat summary cannot exceed 2000 characters")
        return value

    @validates('is_active')
    def validate_is_active(self, key, value):
        if not isinstance(value, bool):
            raise ValueError("is_active must be a boolean")
        return value