from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
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