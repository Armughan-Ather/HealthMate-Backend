from sqlalchemy import (
    Column, Integer, 
    DateTime, ForeignKey, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from constants.enums import RoleEnum


class UserRole(Base):
    __tablename__ = 'user_roles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(Enum(RoleEnum), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="roles")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role', name='uq_user_role'),
        Index('idx_user_role_lookup', 'user_id', 'role'),
    )